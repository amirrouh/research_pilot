"""Browser automation tool using Playwright for web scraping with bot detection avoidance."""

import logging
import random
import time
from typing import Optional
from trion.tools._dependencies import require_package

# Check required packages
require_package("playwright", "web")
require_package("bs4", "web", "beautifulsoup4")

from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright, Browser, Page, TimeoutError as PlaywrightTimeoutError

logger = logging.getLogger(__name__)


def get_content(link: str, timeout: int = 30000, wait_for_selector: Optional[str] = None) -> str:
    """
    Fetch and extract content from a web page using Playwright browser automation.

    Args:
        link: URL to fetch content from
        timeout: Page load timeout in milliseconds (default: 30000)
        wait_for_selector: Optional CSS selector to wait for before extracting content

    Returns:
        Formatted text content of the page

    Raises:
        Exception: If page fails to load or content extraction fails
    """
    logger.info(f"Fetching content from: {link}")

    browser: Optional[Browser] = None

    try:
        with sync_playwright() as p:
            # Launch browser in headless mode
            browser = p.chromium.launch(headless=True)

            # Create context with realistic user agent and viewport
            context = browser.new_context(
                user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                viewport={"width": 1920, "height": 1080}
            )

            # Create new page
            page: Page = context.new_page()

            # Add random delay to avoid bot detection (0-1 seconds)
            delay = random.uniform(0, 1)
            logger.debug(f"Adding random delay: {delay:.2f}s")
            time.sleep(delay)

            # Navigate to the page
            logger.debug(f"Navigating to {link}")
            page.goto(link, timeout=timeout, wait_until="domcontentloaded")

            # Wait for specific selector if provided
            if wait_for_selector:
                logger.debug(f"Waiting for selector: {wait_for_selector}")
                page.wait_for_selector(wait_for_selector, timeout=timeout)

            # Add another small random delay after page load
            time.sleep(random.uniform(0.2, 0.8))

            # Get page content
            html_content = page.content()
            logger.debug("Page content retrieved successfully")

            # Close browser
            browser.close()
            browser = None

            # Parse with BeautifulSoup
            soup = BeautifulSoup(html_content, "lxml")

            # Remove script and style elements
            for element in soup(["script", "style", "meta", "link", "noscript"]):
                element.decompose()

            # Extract text content
            text = soup.get_text(separator="\n", strip=True)

            # Clean up excessive whitespace
            lines = [line.strip() for line in text.splitlines() if line.strip()]
            formatted_content = "\n".join(lines)

            logger.info(f"Successfully extracted {len(formatted_content)} characters from {link}")
            return formatted_content

    except PlaywrightTimeoutError as e:
        logger.error(f"Timeout while loading {link}: {e}")
        raise Exception(f"Page load timeout: {link}") from e

    except Exception as e:
        logger.error(f"Error fetching content from {link}: {e}")
        raise

    finally:
        # Ensure browser is closed even if an error occurred
        if browser:
            try:
                browser.close()
                logger.debug("Browser closed")
            except Exception as e:
                logger.warning(f"Error closing browser: {e}")


def get_content_with_images(
    link: str,
    timeout: int = 30000,
    wait_for_selector: Optional[str] = None
) -> dict:
    """
    Fetch content and extract images from a web page.

    Args:
        link: URL to fetch content from
        timeout: Page load timeout in milliseconds (default: 30000)
        wait_for_selector: Optional CSS selector to wait for before extracting content

    Returns:
        Dictionary with 'text' (formatted content) and 'images' (list of image URLs)
    """
    logger.info(f"Fetching content with images from: {link}")

    browser: Optional[Browser] = None

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)

            context = browser.new_context(
                user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                viewport={"width": 1920, "height": 1080}
            )

            page: Page = context.new_page()

            # Random delay
            time.sleep(random.uniform(0, 1))

            # Navigate
            page.goto(link, timeout=timeout, wait_until="domcontentloaded")

            if wait_for_selector:
                page.wait_for_selector(wait_for_selector, timeout=timeout)

            time.sleep(random.uniform(0.2, 0.8))

            # Get content
            html_content = page.content()

            browser.close()
            browser = None

            # Parse with BeautifulSoup
            soup = BeautifulSoup(html_content, "lxml")

            # Extract images
            images = []
            for img in soup.find_all("img"):
                src = img.get("src")
                if src and isinstance(src, str):
                    # Convert relative URLs to absolute
                    if src.startswith("//"):
                        src = "https:" + src
                    elif src.startswith("/"):
                        from urllib.parse import urljoin
                        src = urljoin(link, src)
                    images.append(src)

            # Remove script and style elements for text extraction
            for element in soup(["script", "style", "meta", "link", "noscript"]):
                element.decompose()

            # Extract text
            text = soup.get_text(separator="\n", strip=True)
            lines = [line.strip() for line in text.splitlines() if line.strip()]
            formatted_content = "\n".join(lines)

            logger.info(f"Extracted {len(formatted_content)} chars and {len(images)} images from {link}")

            return {
                "text": formatted_content,
                "images": images
            }

    except Exception as e:
        logger.error(f"Error fetching content with images from {link}: {e}")
        raise

    finally:
        if browser:
            try:
                browser.close()
            except Exception as e:
                logger.warning(f"Error closing browser: {e}")
