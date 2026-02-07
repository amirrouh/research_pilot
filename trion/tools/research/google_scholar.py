"""
Google Scholar profile scraper.

Fetches all publications from a Google Scholar profile (with pagination support)
and returns author info and publications as JSON.
"""

import re
import time
from typing import Optional, List, Dict
from urllib.parse import parse_qs, urlencode, urlparse

from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright
from langchain.tools import tool


def _extract_scholar_id(url: str) -> Optional[str]:
    """Extract the scholar user ID from a profile URL."""
    parsed = urlparse(url)
    params = parse_qs(parsed.query)
    user_ids = params.get("user", [])
    return user_ids[0] if user_ids else None


def _fetch_page(url: str, wait_for_selector: Optional[str] = None) -> BeautifulSoup:
    """Fetch a page using Playwright and return BeautifulSoup object."""
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(url, wait_until="networkidle")

        if wait_for_selector:
            try:
                page.wait_for_selector(wait_for_selector, timeout=10000)
            except Exception:
                pass

        time.sleep(1)
        content = page.content()
        browser.close()
        return BeautifulSoup(content, "html.parser")


def _parse_author_info(soup: BeautifulSoup, profile_url: str) -> Dict:
    """Extract author information from the profile page."""
    author_info = {
        "scholar_id": _extract_scholar_id(profile_url),
        "profile_url": profile_url,
    }

    name_elem = soup.select_one("#gsc_prf_in")
    author_info["name"] = name_elem.get_text(strip=True) if name_elem else None

    affiliation_elem = soup.select_one(".gsc_prf_il")
    author_info["affiliation"] = affiliation_elem.get_text(strip=True) if affiliation_elem else None

    email_elem = soup.select_one("#gsc_prf_ivh")
    if email_elem:
        email_text = email_elem.get_text(strip=True)
        match = re.search(r"at\s+(.+)", email_text)
        author_info["email_domain"] = match.group(1) if match else None
    else:
        author_info["email_domain"] = None

    metrics = soup.select("#gsc_rsb_st td.gsc_rsb_std")
    if len(metrics) >= 5:
        try:
            author_info["total_citations"] = int(metrics[0].get_text(strip=True).replace(",", ""))
        except (ValueError, IndexError):
            author_info["total_citations"] = None
        try:
            author_info["h_index"] = int(metrics[2].get_text(strip=True))
        except (ValueError, IndexError):
            author_info["h_index"] = None
        try:
            author_info["i10_index"] = int(metrics[4].get_text(strip=True))
        except (ValueError, IndexError):
            author_info["i10_index"] = None
    else:
        author_info["total_citations"] = None
        author_info["h_index"] = None
        author_info["i10_index"] = None

    return author_info


def _parse_publications(soup: BeautifulSoup) -> List[Dict]:
    """Extract publication data from a page."""
    publications = []

    rows = soup.select("tr.gsc_a_tr")
    for row in rows:
        pub = {}

        title_elem = row.select_one("td.gsc_a_t a")
        if title_elem:
            pub["title"] = title_elem.get_text(strip=True)
            href = title_elem.get("href", "")
            if href:
                href_str = str(href)
                pub["scholar_url"] = f"https://scholar.google.com{href_str}" if href_str.startswith("/") else href_str
        else:
            continue

        gray_elems = row.select("td.gsc_a_t .gs_gray")
        if len(gray_elems) >= 1:
            pub["authors"] = gray_elems[0].get_text(strip=True)
        if len(gray_elems) >= 2:
            pub["venue"] = gray_elems[1].get_text(strip=True)

        cite_elem = row.select_one("td.gsc_a_c a")
        if cite_elem:
            cite_text = cite_elem.get_text(strip=True)
            try:
                pub["citations"] = int(cite_text) if cite_text else 0
            except ValueError:
                pub["citations"] = 0
        else:
            pub["citations"] = 0

        year_elem = row.select_one("td.gsc_a_y span")
        if year_elem:
            year_text = year_elem.get_text(strip=True)
            try:
                pub["year"] = int(year_text) if year_text else None
            except ValueError:
                pub["year"] = None
        else:
            pub["year"] = None

        publications.append(pub)

    return publications


def _has_more_pages(soup: BeautifulSoup) -> bool:
    """Check if there are more pages to load."""
    show_more = soup.select_one("#gsc_bpf_more")
    if show_more:
        return not show_more.has_attr("disabled")
    return False


def _get_next_page_url(base_url: str, current_start: int, page_size: int = 100) -> str:
    """Generate the URL for the next page of results."""
    parsed = urlparse(base_url)
    params = parse_qs(parsed.query)
    params["cstart"] = [str(current_start)]
    params["pagesize"] = [str(page_size)]
    new_query = urlencode(params, doseq=True)
    return f"{parsed.scheme}://{parsed.netloc}{parsed.path}?{new_query}"


def fetch_profile(profile_url: str, max_pages: int = 50, verbose: bool = False) -> Dict:
    """
    Fetch all publications from a Google Scholar profile.

    Args:
        profile_url: The Google Scholar profile URL
        max_pages: Maximum number of pages to fetch (safety limit)
        verbose: Print progress messages

    Returns:
        Dictionary with author info and list of publications:
        {
            "author": {
                "name": str,
                "affiliation": str,
                "scholar_id": str,
                "total_citations": int,
                "h_index": int,
                "i10_index": int,
                "profile_url": str,
                "email_domain": str
            },
            "publications": [
                {
                    "title": str,
                    "authors": str,
                    "venue": str,
                    "year": int,
                    "citations": int,
                    "scholar_url": str
                },
                ...
            ]
        }
    """
    if verbose:
        print(f"Fetching Google Scholar profile: {profile_url}")

    soup = _fetch_page(profile_url, wait_for_selector="tr.gsc_a_tr")
    author_info = _parse_author_info(soup, profile_url)

    if verbose:
        print(f"Author: {author_info.get('name')}")
        print(f"Affiliation: {author_info.get('affiliation')}")
        print(f"Citations: {author_info.get('total_citations')}, h-index: {author_info.get('h_index')}")

    all_publications = _parse_publications(soup)
    if verbose:
        print(f"Page 1: Found {len(all_publications)} publications")

    page = 1
    page_size = 100
    current_start = len(all_publications)

    while _has_more_pages(soup) and page < max_pages:
        page += 1
        next_url = _get_next_page_url(profile_url, current_start, page_size)
        if verbose:
            print(f"Fetching page {page}...")
        time.sleep(2)

        soup = _fetch_page(next_url, wait_for_selector="tr.gsc_a_tr")
        page_pubs = _parse_publications(soup)

        if not page_pubs:
            break

        all_publications.extend(page_pubs)
        current_start += len(page_pubs)
        if verbose:
            print(f"Page {page}: Found {len(page_pubs)} publications (total: {len(all_publications)})")

    if verbose:
        print(f"\nTotal publications found: {len(all_publications)}")

    return {
        "author": author_info,
        "publications": all_publications,
    }


# LangChain tool wrapper

@tool
def scrape_scholar_profile(profile_url: str) -> str:
    """
    Scrape a Google Scholar profile and return author info and all publications.

    Use this when you need to collect an author's complete publication list
    from Google Scholar. Handles pagination automatically.

    Args:
        profile_url: Google Scholar profile URL (e.g., https://scholar.google.com/citations?user=...)

    Returns:
        Formatted summary of author info and publications
    """
    try:
        result = fetch_profile(profile_url, verbose=False)

        author = result["author"]
        publications = result["publications"]

        output = [
            f"**{author.get('name', 'Unknown Author')}**",
            f"Affiliation: {author.get('affiliation', 'N/A')}",
            f"Scholar ID: {author.get('scholar_id', 'N/A')}",
            f"Total Citations: {author.get('total_citations', 0):,}",
            f"h-index: {author.get('h_index', 0)}",
            f"i10-index: {author.get('i10_index', 0)}",
            "",
            f"**Publications ({len(publications)} total)**",
            ""
        ]

        # Show top 10 most cited publications
        sorted_pubs = sorted(publications, key=lambda p: p.get('citations', 0), reverse=True)
        for i, pub in enumerate(sorted_pubs[:10], 1):
            output.append(f"{i}. **{pub['title']}**")
            if pub.get('authors'):
                output.append(f"   Authors: {pub['authors']}")
            if pub.get('venue'):
                output.append(f"   Venue: {pub['venue']}")
            if pub.get('year'):
                output.append(f"   Year: {pub['year']}")
            output.append(f"   Citations: {pub.get('citations', 0):,}")
            output.append("")

        if len(publications) > 10:
            output.append(f"... and {len(publications) - 10} more publications")

        return "\n".join(output)

    except Exception as e:
        return f"Error scraping profile: {str(e)}"
