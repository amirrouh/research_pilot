"""
Web Search Tool - DuckDuckGo Search

Simple interface to search the web using DuckDuckGo.

Usage:
    from assistant.tools.web.web_search import duckduckgo_search

    # Basic search
    results = duckduckgo_search("Python programming")

    # Custom number of results
    results = duckduckgo_search("machine learning", max_results=10)

    # Safe search
    results = duckduckgo_search("research topic", safe_search=True)

Returns:
    List of dictionaries with: title, body, href (URL)
"""

import logging
from typing import List, Dict, Optional

from ddgs import DDGS

logger = logging.getLogger(__name__)


def duckduckgo_search(
    query: str,
    max_results: int = 5,
    region: str = "wt-wt",
    safe_search: bool = False,
    timelimit: Optional[str] = None
) -> List[Dict[str, str]]:
    """
    Search the web using DuckDuckGo.

    Args:
        query: Search query string
        max_results: Maximum number of results to return (default: 5)
        region: Region for search results (default: "wt-wt" for worldwide)
               Examples: "us-en", "uk-en", "de-de"
        safe_search: Enable safe search filtering (default: False)
        timelimit: Time filter for results (optional)
                  Options: "d" (day), "w" (week), "m" (month), "y" (year)

    Returns:
        List of dictionaries containing:
            - title: Page title
            - body: Snippet/description
            - href: URL

    Raises:
        Exception: If search fails
    """
    logger.info(f"Searching DuckDuckGo for: {query} (max_results={max_results})")

    try:
        # Create DDGS instance
        ddgs = DDGS()

        # Perform search
        results = list(ddgs.text(
            query=query,
            region=region,
            safesearch="on" if safe_search else "off",
            timelimit=timelimit,
            max_results=max_results
        ))

        logger.info(f"Found {len(results)} results for query: {query}")

        # Clean and format results
        formatted_results = []
        for result in results:
            formatted_results.append({
                "title": result.get("title", ""),
                "body": result.get("body", ""),
                "href": result.get("href", "")
            })

        return formatted_results

    except Exception as e:
        logger.error(f"Error searching DuckDuckGo for '{query}': {e}")
        raise Exception(f"DuckDuckGo search failed: {e}") from e


def duckduckgo_news_search(
    query: str,
    max_results: int = 5,
    region: str = "wt-wt",
    safe_search: bool = False,
    timelimit: Optional[str] = None
) -> List[Dict[str, str]]:
    """
    Search news articles using DuckDuckGo News.

    Args:
        query: Search query string
        max_results: Maximum number of results to return (default: 5)
        region: Region for search results (default: "wt-wt" for worldwide)
        safe_search: Enable safe search filtering (default: False)
        timelimit: Time filter for results (optional)
                  Options: "d" (day), "w" (week), "m" (month)

    Returns:
        List of dictionaries containing:
            - title: Article title
            - body: Article snippet
            - href: URL
            - date: Publication date
            - source: News source

    Raises:
        Exception: If search fails
    """
    logger.info(f"Searching DuckDuckGo News for: {query} (max_results={max_results})")

    try:
        ddgs = DDGS()

        # Perform news search
        results = list(ddgs.news(
            query=query,
            region=region,
            safesearch="on" if safe_search else "off",
            timelimit=timelimit,
            max_results=max_results
        ))

        logger.info(f"Found {len(results)} news results for query: {query}")

        # Clean and format results
        formatted_results = []
        for result in results:
            formatted_results.append({
                "title": result.get("title", ""),
                "body": result.get("body", ""),
                "href": result.get("url", ""),
                "date": result.get("date", ""),
                "source": result.get("source", "")
            })

        return formatted_results

    except Exception as e:
        logger.error(f"Error searching DuckDuckGo News for '{query}': {e}")
        raise Exception(f"DuckDuckGo news search failed: {e}") from e


# LangChain Tool Wrappers
try:
    from langchain.tools import tool

    @tool
    def web_search(query: str, max_results: int = 5) -> str:
        """
        Search the web using DuckDuckGo.

        Use this tool when you need to find current information from the internet,
        look up facts, find websites, or research topics not in your training data.

        Args:
            query: What to search for
            max_results: Number of results to return (default: 5, max: 10)

        Returns:
            Formatted search results with titles, descriptions, and URLs
        """
        results = duckduckgo_search(query, min(max_results, 10))

        if not results:
            return f"No results found for: {query}"

        output = [f"Web search results for '{query}':\n"]
        for i, result in enumerate(results, 1):
            output.append(
                f"{i}. {result['title']}\n"
                f"   {result['body']}\n"
                f"   URL: {result['href']}\n"
            )

        return "\n".join(output)

    @tool
    def news_search(query: str, max_results: int = 5, timeframe: str = "w") -> str:
        """
        Search for recent news articles using DuckDuckGo News.

        Use this tool when you need current news, recent events, or timely information
        about a topic.

        Args:
            query: What news to search for
            max_results: Number of results to return (default: 5, max: 10)
            timeframe: Time filter - "d" (day), "w" (week), "m" (month) (default: "w")

        Returns:
            Formatted news results with titles, snippets, sources, and URLs
        """
        # Validate timeframe
        valid_timeframes = ["d", "w", "m"]
        if timeframe not in valid_timeframes:
            timeframe = "w"

        results = duckduckgo_news_search(query, min(max_results, 10), timelimit=timeframe)

        if not results:
            return f"No news found for: {query}"

        output = [f"News search results for '{query}' (last {timeframe}):\n"]
        for i, result in enumerate(results, 1):
            output.append(
                f"{i}. {result['title']}\n"
                f"   {result['body']}\n"
                f"   Source: {result['source']} | Date: {result['date']}\n"
                f"   URL: {result['href']}\n"
            )

        return "\n".join(output)

except ImportError:
    # LangChain not installed - skip tool creation
    pass


# Test
if __name__ == "__main__":
    import json

    # Setup logging for tests
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

    print("\n" + "="*100)
    print("Example 1: Basic web search")
    print("="*100)
    results = duckduckgo_search("Python programming tutorial", max_results=3)
    print(json.dumps(results, indent=2))

    print("\n" + "="*100)
    print("Example 2: News search")
    print("="*100)
    results = duckduckgo_news_search("artificial intelligence", max_results=3, timelimit="d")
    print(json.dumps(results, indent=2))

    print("\n" + "="*100)
    print("Example 3: Recent results only")
    print("="*100)
    results = duckduckgo_search("Claude AI", max_results=3, timelimit="w")
    print(json.dumps(results, indent=2))

    print("\n✅ Tests completed!")
