"""
Search Academic Articles - Standalone Module

Simple interface to search PubMed and arXiv for academic papers.

Usage:
    from tools.search_articles import query

    # Basic search
    results = query(keywords="CRISPR")

    # Custom counts per source
    results = query(keywords="machine learning", sources=[('pubmed', 10), ('arxiv', 5)])

    # Filter recent papers
    results = query(keywords="COVID-19", recent_years=2)

    # Search by title
    results = query(title="Deep learning", keywords="genomics")

Returns:
    pandas.DataFrame with columns: title, authors, year, journal, doi, pmid,
    abstract, url, source, etc.
"""
import pandas as pd
from Bio import Entrez
import arxiv
from datetime import datetime
from typing import Optional, List, Tuple, Union

# Set email for PubMed (required)
Entrez.email = "your.email@example.com"


def _search_pubmed(keywords: str, count: int, min_year: Optional[int] = None) -> list:
    """Search PubMed for articles"""
    try:
        # Build search term with year filter if specified
        search_term = keywords
        if min_year:
            search_term = f"{keywords} AND {min_year}:3000[dp]"

        # Search PubMed
        search_handle = Entrez.esearch(
            db="pubmed",
            term=search_term,
            retmax=count,
            sort="pub_date"
        )
        search_results = Entrez.read(search_handle)
        search_handle.close()

        id_list = search_results["IdList"]
        if not id_list:
            return []

        # Fetch article details
        fetch_handle = Entrez.efetch(
            db="pubmed",
            id=id_list,
            rettype="xml",
            retmode="xml"
        )
        records = Entrez.read(fetch_handle)
        fetch_handle.close()

        articles = []
        for record in records['PubmedArticle']:
            article = record['MedlineCitation']['Article']
            medline = record['MedlineCitation']

            # Extract PMID
            pmid = str(medline.get('PMID', 'N/A'))

            # Extract authors
            authors = []
            if 'AuthorList' in article:
                for author in article['AuthorList']:
                    if 'LastName' in author:
                        lastname = author['LastName']
                        firstname = author.get('ForeName', author.get('Initials', ''))
                        authors.append(f"{lastname}, {firstname}")
            authors_str = "; ".join(authors) if authors else "N/A"

            # Extract publication date
            pub_date = article.get('Journal', {}).get('JournalIssue', {}).get('PubDate', {})
            year = pub_date.get('Year', 'N/A')
            month = pub_date.get('Month', '')
            day = pub_date.get('Day', '')
            date_str = f"{year}-{month}-{day}" if month else year

            # Extract journal info
            journal_info = article.get('Journal', {})
            journal = journal_info.get('Title', 'N/A')
            volume = journal_info.get('JournalIssue', {}).get('Volume', 'N/A')
            issue = journal_info.get('JournalIssue', {}).get('Issue', 'N/A')

            # Extract pagination
            pagination = article.get('Pagination', {})
            pages = pagination.get('MedlinePgn', 'N/A')

            # Extract DOI
            doi = 'N/A'
            if 'ELocationID' in article:
                for eloc in article['ELocationID']:
                    if eloc.attributes.get('EIdType') == 'doi':
                        doi = str(eloc)
                        break

            # Extract abstract
            abstract = 'N/A'
            if 'Abstract' in article and 'AbstractText' in article['Abstract']:
                abstract_parts = article['Abstract']['AbstractText']
                if isinstance(abstract_parts, list):
                    abstract = " ".join([str(part) for part in abstract_parts])
                else:
                    abstract = str(abstract_parts)

            # Build URLs
            pmid_url = f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/"
            doi_url = f"https://doi.org/{doi}" if doi != 'N/A' else 'N/A'

            articles.append({
                'title': article.get('ArticleTitle', 'N/A'),
                'authors': authors_str,
                'year': year,
                'journal': journal,
                'volume': volume,
                'issue': issue,
                'pages': pages,
                'doi': doi,
                'pmid': pmid,
                'abstract': abstract,
                'date': date_str,
                'url': pmid_url,
                'doi_url': doi_url,
                'source': 'PubMed'
            })

        return articles
    except Exception as e:
        print(f"PubMed error: {e}")
        return []


def _search_arxiv(keywords: str, count: int, min_year: Optional[int] = None) -> list:
    """Search arXiv for articles"""
    try:
        client = arxiv.Client()
        search = arxiv.Search(
            query=keywords,
            max_results=count * 2 if min_year else count,
            sort_by=arxiv.SortCriterion.SubmittedDate
        )

        articles = []
        for result in client.results(search):
            # Filter by year if specified
            if min_year and result.published.year < min_year:
                continue

            # Extract authors
            authors_list = [a.name for a in result.authors]
            authors_str = "; ".join(authors_list)

            # Extract arXiv ID
            arxiv_id = result.entry_id.split('/')[-1]

            # Extract dates
            year = result.published.year
            date_str = result.published.strftime('%Y-%m-%d')

            # Extract DOI if available
            doi = result.doi if result.doi else 'N/A'
            doi_url = f"https://doi.org/{doi}" if doi != 'N/A' else 'N/A'

            # Extract primary category
            category = result.primary_category

            articles.append({
                'title': result.title.replace('\n', ' '),
                'authors': authors_str,
                'year': str(year),
                'journal': f"arXiv ({category})",
                'volume': 'N/A',
                'issue': 'N/A',
                'pages': 'N/A',
                'doi': doi,
                'pmid': 'N/A',
                'abstract': result.summary.replace('\n', ' '),
                'date': date_str,
                'url': result.entry_id,
                'doi_url': doi_url,
                'arxiv_id': arxiv_id,
                'source': 'arXiv'
            })

            if len(articles) >= count:
                break

        return articles
    except Exception as e:
        print(f"arXiv error: {e}")
        return []


def query(
    keywords: Optional[str] = None,
    title: Optional[str] = None,
    sources: Optional[Union[List[str], List[Tuple[str, int]]]] = None,
    recent_years: Optional[int] = None
) -> pd.DataFrame:
    """
    Search academic articles from reliable sources (PubMed and arXiv).

    Args:
        keywords: Search terms (searches in title, abstract, etc.)
        title: Specific title search (can be combined with keywords)
        sources: List of sources to search. Can be:
                 - ['pubmed', 'arxiv']: Equal split between sources
                 - [('pubmed', 10), ('arxiv', 5)]: Specific counts per source
                 Default: equal split (5 each)
        recent_years: Filter to only articles from last N years (e.g., 5 = last 5 years)

    Returns:
        DataFrame with article information

    Examples:
        query(keywords="CRISPR")
        query(keywords="machine learning", sources=[('pubmed', 10), ('arxiv', 5)])
        query(keywords="COVID-19", recent_years=2)
        query(title="Deep learning", keywords="genomics")
    """
    # Build search query
    search_query = ""
    if title and keywords:
        search_query = f"{title} {keywords}"
    elif title:
        search_query = title
    elif keywords:
        search_query = keywords
    else:
        raise ValueError("Must provide at least one of: keywords or title")

    # Calculate minimum year if recent_years is specified
    min_year = None
    if recent_years:
        current_year = datetime.now().year
        min_year = current_year - recent_years

    # Parse sources parameter
    if sources is None:
        source_config = [('pubmed', 5), ('arxiv', 5)]
    elif isinstance(sources, list) and len(sources) > 0:
        if isinstance(sources[0], tuple):
            source_config = sources
        else:
            count_per_source = 10 // len(sources)
            source_config = [(src, count_per_source) for src in sources]
    else:
        source_config = [('pubmed', 5), ('arxiv', 5)]

    # Search each source
    all_articles = []
    for source_name, count in source_config:
        source_lower = source_name.lower()

        if source_lower == 'pubmed':
            articles = _search_pubmed(search_query, count, min_year)
            all_articles.extend(articles)
        elif source_lower == 'arxiv':
            articles = _search_arxiv(search_query, count, min_year)
            all_articles.extend(articles)
        else:
            print(f"⚠️ Unknown source '{source_name}' - skipping. Valid: 'pubmed', 'arxiv'")

    # Create DataFrame
    if not all_articles:
        columns = ['title', 'authors', 'year', 'journal', 'volume', 'issue',
                   'pages', 'doi', 'pmid', 'abstract', 'date', 'url', 'doi_url', 'source']
        return pd.DataFrame(columns=columns)

    df = pd.DataFrame(all_articles)

    # Reorder columns
    column_order = ['title', 'authors', 'year', 'journal', 'volume', 'issue',
                    'pages', 'doi', 'pmid', 'date', 'url', 'doi_url', 'abstract', 'source']
    column_order = [col for col in column_order if col in df.columns]
    df = df[column_order]

    return df


def get_paper_details(paper_id: str, source: str) -> dict:
    """
    Get full details for a specific paper.

    Args:
        paper_id: Paper identifier (PMID for PubMed, arXiv ID for arXiv)
        source: 'pubmed' or 'arxiv'

    Returns:
        Dictionary with complete paper details including abstract, authors, journal, DOI, etc.

    Examples:
        get_paper_details("38234567", "pubmed")
        get_paper_details("2301.07041", "arxiv")
    """
    source_lower = source.lower()

    if source_lower == 'pubmed':
        try:
            # Fetch article details
            fetch_handle = Entrez.efetch(
                db="pubmed",
                id=paper_id,
                rettype="xml",
                retmode="xml"
            )
            records = Entrez.read(fetch_handle)
            fetch_handle.close()

            if not records.get('PubmedArticle'):
                return {"error": f"No article found with PMID: {paper_id}"}

            record = records['PubmedArticle'][0]
            article = record['MedlineCitation']['Article']
            medline = record['MedlineCitation']

            # Extract all details (reusing logic from _search_pubmed)
            pmid = str(medline.get('PMID', 'N/A'))

            # Authors
            authors = []
            if 'AuthorList' in article:
                for author in article['AuthorList']:
                    if 'LastName' in author:
                        lastname = author['LastName']
                        firstname = author.get('ForeName', author.get('Initials', ''))
                        authors.append(f"{lastname}, {firstname}")

            # Publication date
            pub_date = article.get('Journal', {}).get('JournalIssue', {}).get('PubDate', {})
            year = pub_date.get('Year', 'N/A')
            month = pub_date.get('Month', '')
            day = pub_date.get('Day', '')
            date_str = f"{year}-{month}-{day}" if month else year

            # Journal info
            journal_info = article.get('Journal', {})
            journal = journal_info.get('Title', 'N/A')
            volume = journal_info.get('JournalIssue', {}).get('Volume', 'N/A')
            issue = journal_info.get('JournalIssue', {}).get('Issue', 'N/A')

            # Pagination
            pagination = article.get('Pagination', {})
            pages = pagination.get('MedlinePgn', 'N/A')

            # DOI
            doi = 'N/A'
            if 'ELocationID' in article:
                for eloc in article['ELocationID']:
                    if eloc.attributes.get('EIdType') == 'doi':
                        doi = str(eloc)
                        break

            # Abstract
            abstract = 'N/A'
            if 'Abstract' in article and 'AbstractText' in article['Abstract']:
                abstract_parts = article['Abstract']['AbstractText']
                if isinstance(abstract_parts, list):
                    abstract = " ".join([str(part) for part in abstract_parts])
                else:
                    abstract = str(abstract_parts)

            # Keywords
            keywords = []
            if 'KeywordList' in medline:
                for keyword_list in medline['KeywordList']:
                    keywords.extend([str(kw) for kw in keyword_list])

            return {
                'pmid': pmid,
                'title': article.get('ArticleTitle', 'N/A'),
                'authors': authors,
                'year': year,
                'date': date_str,
                'journal': journal,
                'volume': volume,
                'issue': issue,
                'pages': pages,
                'doi': doi,
                'abstract': abstract,
                'keywords': keywords,
                'url': f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/",
                'doi_url': f"https://doi.org/{doi}" if doi != 'N/A' else 'N/A',
                'source': 'PubMed'
            }

        except Exception as e:
            return {"error": f"PubMed error: {e}"}

    elif source_lower == 'arxiv':
        try:
            client = arxiv.Client()
            search = arxiv.Search(id_list=[paper_id])
            result = next(client.results(search))

            # Extract authors
            authors = [a.name for a in result.authors]

            # Extract dates
            year = result.published.year
            date_str = result.published.strftime('%Y-%m-%d')

            # Extract DOI if available
            doi = result.doi if result.doi else 'N/A'

            # Categories
            categories = [result.primary_category] + list(result.categories)

            return {
                'arxiv_id': paper_id,
                'title': result.title.replace('\n', ' '),
                'authors': authors,
                'year': str(year),
                'date': date_str,
                'journal': f"arXiv ({result.primary_category})",
                'doi': doi,
                'abstract': result.summary.replace('\n', ' '),
                'categories': categories,
                'url': result.entry_id,
                'doi_url': f"https://doi.org/{doi}" if doi != 'N/A' else 'N/A',
                'pdf_url': result.pdf_url,
                'source': 'arXiv'
            }

        except Exception as e:
            return {"error": f"arXiv error: {e}"}

    else:
        return {"error": f"Unknown source '{source}'. Valid: 'pubmed', 'arxiv'"}


def find_related_papers(paper_id: str, source: str, count: int = 5) -> list:
    """
    Find papers related to a specific paper.

    Args:
        paper_id: Paper identifier (PMID for PubMed, arXiv ID for arXiv)
        source: 'pubmed' or 'arxiv'
        count: Number of related papers to return (default: 5)

    Returns:
        List of dictionaries with related paper information

    Examples:
        find_related_papers("38234567", "pubmed", count=5)
        find_related_papers("2301.07041", "arxiv", count=5)
    """
    source_lower = source.lower()

    if source_lower == 'pubmed':
        try:
            # Use elink to find similar articles
            link_handle = Entrez.elink(
                dbfrom="pubmed",
                db="pubmed",
                id=paper_id,
                linkname="pubmed_pubmed",
                cmd="neighbor_score"
            )
            link_results = Entrez.read(link_handle)
            link_handle.close()

            if not link_results or not link_results[0].get('LinkSetDb'):
                return []

            # Get related PMIDs
            related_ids = []
            for link in link_results[0]['LinkSetDb'][0]['Link'][:count]:
                related_ids.append(link['Id'])

            if not related_ids:
                return []

            # Fetch details for related papers
            fetch_handle = Entrez.efetch(
                db="pubmed",
                id=related_ids,
                rettype="xml",
                retmode="xml"
            )
            records = Entrez.read(fetch_handle)
            fetch_handle.close()

            related_papers = []
            for record in records['PubmedArticle']:
                article = record['MedlineCitation']['Article']
                medline = record['MedlineCitation']
                pmid = str(medline.get('PMID', 'N/A'))

                # Extract authors
                authors = []
                if 'AuthorList' in article:
                    for author in article['AuthorList'][:3]:  # First 3 authors
                        if 'LastName' in author:
                            lastname = author['LastName']
                            firstname = author.get('ForeName', author.get('Initials', ''))
                            authors.append(f"{lastname}, {firstname}")

                # Extract year
                pub_date = article.get('Journal', {}).get('JournalIssue', {}).get('PubDate', {})
                year = pub_date.get('Year', 'N/A')

                # Extract journal
                journal = article.get('Journal', {}).get('Title', 'N/A')

                related_papers.append({
                    'pmid': pmid,
                    'title': article.get('ArticleTitle', 'N/A'),
                    'authors': "; ".join(authors),
                    'year': year,
                    'journal': journal,
                    'url': f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/",
                    'source': 'PubMed'
                })

            return related_papers

        except Exception as e:
            return [{"error": f"PubMed error: {e}"}]

    elif source_lower == 'arxiv':
        try:
            # First get the original paper's categories
            paper_details = get_paper_details(paper_id, 'arxiv')
            if 'error' in paper_details:
                return [paper_details]

            primary_category = paper_details.get('categories', ['cs.AI'])[0]

            # Search for papers in the same category
            client = arxiv.Client()
            search = arxiv.Search(
                query=f"cat:{primary_category}",
                max_results=count + 10,  # Get extra to filter out the original
                sort_by=arxiv.SortCriterion.Relevance
            )

            related_papers = []
            for result in client.results(search):
                arxiv_id = result.entry_id.split('/')[-1]

                # Skip the original paper
                if arxiv_id == paper_id:
                    continue

                # Extract authors
                authors = [a.name for a in result.authors[:3]]  # First 3 authors

                related_papers.append({
                    'arxiv_id': arxiv_id,
                    'title': result.title.replace('\n', ' '),
                    'authors': "; ".join(authors),
                    'year': str(result.published.year),
                    'journal': f"arXiv ({result.primary_category})",
                    'url': result.entry_id,
                    'source': 'arXiv'
                })

                if len(related_papers) >= count:
                    break

            return related_papers

        except Exception as e:
            return [{"error": f"arXiv error: {e}"}]

    else:
        return [{"error": f"Unknown source '{source}'. Valid: 'pubmed', 'arxiv'"}]


def get_citations(paper_id: str, source: str) -> dict:
    """
    Get citation information for a paper.

    Args:
        paper_id: Paper identifier (PMID for PubMed, arXiv ID for arXiv)
        source: 'pubmed' or 'arxiv'

    Returns:
        Dictionary with citation count and list of citing papers (if available)

    Examples:
        get_citations("38234567", "pubmed")
        get_citations("2301.07041", "arxiv")

    Note:
        - PubMed: Uses PubMed Central citation data (may be limited)
        - arXiv: Citation tracking not available (arXiv doesn't track citations)
    """
    source_lower = source.lower()

    if source_lower == 'pubmed':
        try:
            # Use elink to find papers that cite this one
            link_handle = Entrez.elink(
                dbfrom="pubmed",
                db="pubmed",
                id=paper_id,
                linkname="pubmed_pubmed_citedin"
            )
            link_results = Entrez.read(link_handle)
            link_handle.close()

            citing_papers = []
            citation_count = 0

            if link_results and link_results[0].get('LinkSetDb'):
                # Get citing PMIDs
                citing_ids = [link['Id'] for link in link_results[0]['LinkSetDb'][0]['Link']]
                citation_count = len(citing_ids)

                if citing_ids:
                    # Fetch details for citing papers (limit to 10)
                    fetch_handle = Entrez.efetch(
                        db="pubmed",
                        id=citing_ids[:10],
                        rettype="xml",
                        retmode="xml"
                    )
                    records = Entrez.read(fetch_handle)
                    fetch_handle.close()

                    for record in records['PubmedArticle']:
                        article = record['MedlineCitation']['Article']
                        medline = record['MedlineCitation']
                        pmid = str(medline.get('PMID', 'N/A'))

                        # Extract authors (first 3)
                        authors = []
                        if 'AuthorList' in article:
                            for author in article['AuthorList'][:3]:
                                if 'LastName' in author:
                                    lastname = author['LastName']
                                    firstname = author.get('ForeName', author.get('Initials', ''))
                                    authors.append(f"{lastname}, {firstname}")

                        # Extract year
                        pub_date = article.get('Journal', {}).get('JournalIssue', {}).get('PubDate', {})
                        year = pub_date.get('Year', 'N/A')

                        citing_papers.append({
                            'pmid': pmid,
                            'title': article.get('ArticleTitle', 'N/A'),
                            'authors': "; ".join(authors),
                            'year': year,
                            'url': f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/"
                        })

            return {
                'paper_id': paper_id,
                'source': 'PubMed',
                'citation_count': citation_count,
                'citing_papers': citing_papers,
                'note': 'Citation data from PubMed Central (may be incomplete)'
            }

        except Exception as e:
            return {"error": f"PubMed error: {e}"}

    elif source_lower == 'arxiv':
        return {
            'paper_id': paper_id,
            'source': 'arXiv',
            'citation_count': 'N/A',
            'citing_papers': [],
            'note': 'arXiv does not provide citation tracking. Consider using external services like Semantic Scholar or Google Scholar.'
        }

    else:
        return {"error": f"Unknown source '{source}'. Valid: 'pubmed', 'arxiv'"}


def format_citation(row, style='APA'):
    """
    Format a citation from a DataFrame row.

    Args:
        row: DataFrame row with article info
        style: Citation style ('APA', 'Vancouver')

    Returns:
        Formatted citation string
    """
    if style == 'APA':
        authors = row['authors'].replace('; ', ', ')
        year = row['year']
        title = row['title']
        journal = row['journal']
        volume = row['volume']
        issue = row['issue']
        pages = row['pages']
        doi = row['doi']

        citation = f"{authors} ({year}). {title}. {journal}"
        if volume != 'N/A':
            citation += f", {volume}"
        if issue != 'N/A':
            citation += f"({issue})"
        if pages != 'N/A':
            citation += f", {pages}"
        if doi != 'N/A':
            citation += f". https://doi.org/{doi}"
        else:
            citation += f". {row['url']}"

        return citation

    elif style == 'Vancouver':
        authors = row['authors'].split('; ')[:3]
        authors_str = ', '.join(authors)
        if len(row['authors'].split('; ')) > 3:
            authors_str += ', et al'

        year = row['year']
        title = row['title']
        journal = row['journal']
        volume = row['volume']
        pages = row['pages']

        citation = f"{authors_str}. {title}. {journal}. {year}"
        if volume != 'N/A':
            citation += f";{volume}"
        if pages != 'N/A':
            citation += f":{pages}"
        citation += "."

        return citation

    else:
        return f"{row['authors']} ({row['year']}). {row['title']}. {row['journal']}."


# LangChain Tool Wrapper
try:
    from langchain_core.tools import tool

    @tool
    def search_papers(keywords: str, pubmed_count: int = 3, arxiv_count: int = 3) -> str:
        """
        Search academic papers from specialized databases.

        IMPORTANT - Choose the right source:
        - PubMed: Medical, biological, health sciences (e.g., "cancer research", "CRISPR", "drug development")
        - arXiv: Computer science, AI, physics, math (e.g., "neural networks", "machine learning", "quantum computing")

        For AI/ML/CS topics: Set pubmed_count=0 and increase arxiv_count
        For medical/bio topics: Set arxiv_count=0 and increase pubmed_count

        Args:
            keywords: Search terms (e.g., "CRISPR gene editing", "neural networks")
            pubmed_count: Number of PubMed papers (0-10, default: 3) - Use 0 for non-medical topics
            arxiv_count: Number of arXiv papers (0-10, default: 3) - Use 0 for non-CS topics

        Returns:
            Formatted list of papers with titles, authors, years, and sources
        """
        results = query(keywords=keywords, sources=[('pubmed', pubmed_count), ('arxiv', arxiv_count)])

        if len(results) == 0:
            return f"No papers found for: {keywords}"

        output = [f"Found {len(results)} papers for '{keywords}':\n"]
        for i, row in results.iterrows():
            output.append(
                f"{i+1}. {row['title']}\n"
                f"   Authors: {row['authors'][:100]}...\n"
                f"   Year: {row['year']} | Source: {row['source']}\n"
                f"   URL: {row['url']}\n"
            )
        return "\n".join(output)

    @tool
    def get_paper_info(paper_id: str, source: str) -> str:
        """
        Get complete details for a specific academic paper.

        Use this when you have a paper ID and need full information including abstract,
        authors, journal, DOI, publication date, and keywords.

        Args:
            paper_id: Paper identifier (PMID for PubMed like "38234567", or arXiv ID like "2301.07041")
            source: Database source - either "pubmed" or "arxiv"

        Returns:
            Formatted paper details including title, authors, abstract, journal, etc.
        """
        details = get_paper_details(paper_id, source)

        if 'error' in details:
            return f"Error: {details['error']}"

        output = [f"Paper Details ({details['source']}):\n"]
        output.append(f"Title: {details['title']}")

        # Format authors
        if isinstance(details['authors'], list):
            authors_str = "; ".join(details['authors'][:5])
            if len(details['authors']) > 5:
                authors_str += f" (and {len(details['authors']) - 5} more)"
        else:
            authors_str = details['authors']
        output.append(f"Authors: {authors_str}")

        output.append(f"Year: {details['year']}")
        output.append(f"Journal: {details['journal']}")

        if details.get('doi') != 'N/A':
            output.append(f"DOI: {details['doi']}")

        if details.get('abstract') and details['abstract'] != 'N/A':
            abstract = details['abstract'][:500] + "..." if len(details['abstract']) > 500 else details['abstract']
            output.append(f"\nAbstract: {abstract}")

        if details.get('keywords'):
            output.append(f"Keywords: {', '.join(details['keywords'][:10])}")

        output.append(f"\nURL: {details['url']}")

        return "\n".join(output)

    @tool
    def find_similar_papers(paper_id: str, source: str, count: int = 5) -> str:
        """
        Find papers similar to a given paper.

        Use this to discover related research based on a paper you already know about.
        For PubMed, uses their "Similar articles" algorithm.
        For arXiv, finds papers in the same category.

        Args:
            paper_id: Paper identifier (PMID for PubMed like "38234567", or arXiv ID like "2301.07041")
            source: Database source - either "pubmed" or "arxiv"
            count: Number of similar papers to find (default: 5, max: 10)

        Returns:
            Formatted list of similar papers with titles, authors, and years
        """
        related = find_related_papers(paper_id, source, min(count, 10))

        if not related:
            return f"No related papers found for {source} ID: {paper_id}"

        if isinstance(related, list) and len(related) > 0 and 'error' in related[0]:
            return f"Error: {related[0]['error']}"

        output = [f"Found {len(related)} papers related to {source} ID {paper_id}:\n"]
        for i, paper in enumerate(related, 1):
            output.append(
                f"{i}. {paper['title']}\n"
                f"   Authors: {paper['authors']}\n"
                f"   Year: {paper['year']} | {paper['source']}\n"
                f"   URL: {paper['url']}\n"
            )

        return "\n".join(output)

    @tool
    def get_paper_citations(paper_id: str, source: str) -> str:
        """
        Get citation information for a paper (how many times it's been cited and by whom).

        Use this to track paper impact and find newer research building on this work.
        Note: PubMed data may be incomplete. arXiv does not track citations.

        Args:
            paper_id: Paper identifier (PMID for PubMed like "38234567", or arXiv ID like "2301.07041")
            source: Database source - either "pubmed" or "arxiv"

        Returns:
            Citation count and list of citing papers (if available)
        """
        citation_data = get_citations(paper_id, source)

        if 'error' in citation_data:
            return f"Error: {citation_data['error']}"

        output = [f"Citation Information for {citation_data['source']} ID {citation_data['paper_id']}:\n"]
        output.append(f"Citation Count: {citation_data['citation_count']}")

        if citation_data.get('note'):
            output.append(f"Note: {citation_data['note']}")

        citing_papers = citation_data.get('citing_papers', [])
        if citing_papers:
            output.append(f"\nSample of Citing Papers ({len(citing_papers)} shown):")
            for i, paper in enumerate(citing_papers, 1):
                output.append(
                    f"\n{i}. {paper['title']}\n"
                    f"   Authors: {paper['authors']}\n"
                    f"   Year: {paper['year']}\n"
                    f"   URL: {paper['url']}"
                )
        else:
            output.append("\nNo citing papers found in the database.")

        return "\n".join(output)

except ImportError:
    # LangChain not installed - skip tool creation
    pass


# Test
if __name__ == "__main__":
    pd.set_option('display.max_colwidth', 60)
    pd.set_option('display.width', 200)

    print("\n" + "="*100)
    print("Example 1: Basic search")
    print("="*100)
    results = query(keywords="CRISPR", sources=[('pubmed', 3), ('arxiv', 2)])
    print(results[['title', 'year', 'journal', 'source']].to_string(index=False))

    print("\n" + "="*100)
    print("Example 2: Recent years filter")
    print("="*100)
    results = query(keywords="COVID-19", sources=[('pubmed', 3)], recent_years=2)
    print(results[['title', 'year', 'source']].to_string(index=False))

    print("\n✅ Tests completed!")


