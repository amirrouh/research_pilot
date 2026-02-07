"""
Download Tool - Download files from URLs

Simple interface to download files from the web.

Usage:
    from assistant.tools.web.download import download

    # Download file
    download("https://example.com/file.pdf", "downloads/file.pdf")

Returns:
    str: Path to downloaded file
"""

import requests
from typing import Union
from pathlib import Path


def download(
    url: str,
    save_path: Union[str, Path],
    timeout: int = 30
) -> str:
    """
    Download a file from a URL.

    Args:
        url: URL to download from
        save_path: Where to save the file (absolute or relative path)
        timeout: Request timeout in seconds (default: 30)

    Returns:
        Path to the downloaded file

    Examples:
        download("https://example.com/paper.pdf", "papers/paper.pdf")
        download("https://example.com/image.jpg", "images/image.jpg")
    """
    # Convert to Path
    save_path = Path(save_path)

    # Create parent directory if it doesn't exist
    save_path.parent.mkdir(parents=True, exist_ok=True)

    # Download file
    response = requests.get(url, timeout=timeout, stream=True)
    response.raise_for_status()

    # Write to file
    with open(save_path, 'wb') as f:
        for chunk in response.iter_content(chunk_size=8192):
            if chunk:
                f.write(chunk)

    return str(save_path.absolute())


# LangChain Tool Wrapper
try:
    from langchain_core.tools import tool

    @tool
    def download_file(url: str, save_path: str) -> str:
        """
        Download a file from a URL to a local path.

        Use this tool when you need to:
        - Download files from the internet
        - Save PDFs, images, documents, or any file type
        - Get files from direct download links

        Args:
            url: The URL to download from (must be a direct download link)
            save_path: Where to save the file (e.g., "downloads/file.pdf")

        Returns:
            Absolute path to the downloaded file
        """
        result = download(url, save_path)
        return f"Downloaded to: {result}"

except ImportError:
    # LangChain not installed - skip tool creation
    pass


# Test
if __name__ == "__main__":
    import sys

    if len(sys.argv) < 3:
        print("Usage: python download.py <url> <save_path>")
        print("\nExample:")
        print("  python download.py https://example.com/file.pdf downloads/file.pdf")
        sys.exit(1)

    url = sys.argv[1]
    save_path = sys.argv[2]

    print(f"\n{'='*80}")
    print(f"Downloading: {url}")
    print(f"Saving to: {save_path}")
    print(f"{'='*80}\n")

    try:
        result = download(url, save_path)
        print(f"✅ Downloaded successfully!")
        print(f"Location: {result}")
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)

    print(f"\n{'='*80}\n")
