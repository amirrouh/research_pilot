"""
File Read Tool - Read files from disk

Simple interface to read text files.

Usage:
    from trion.tools.document.read import read

    # Read file
    content = read("document.txt")

Returns:
    str: File content
"""

from typing import Union, Optional
from pathlib import Path


def read(
    file_path: Union[str, Path],
    encoding: str = "utf-8"
) -> str:
    """
    Read a text file.

    Args:
        file_path: Path to the file to read
        encoding: File encoding (default: utf-8)

    Returns:
        File content as string

    Examples:
        read("document.txt")
        read("data.json")
        read("paper.md")
    """
    file_path = Path(file_path)

    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")

    with open(file_path, 'r', encoding=encoding) as f:
        return f.read()


# LangChain Tool Wrapper
try:
    from langchain_core.tools import tool

    @tool
    def read_file(file_path: str) -> str:
        """
        Read a text file from disk.

        Use this tool when you need to:
        - Read content from text files
        - Load documents, notes, or data
        - Access file contents

        Supports: txt, md, json, csv, xml, html, py, etc.

        Args:
            file_path: Path to the file to read

        Returns:
            Content of the file as text
        """
        result = read(file_path)
        return result

except ImportError:
    # LangChain not installed - skip tool creation
    pass


# Test
if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: python read.py <file_path>")
        print("\nExample:")
        print("  python read.py document.txt")
        sys.exit(1)

    file_path = sys.argv[1]

    print(f"\n{'='*80}")
    print(f"Reading: {file_path}")
    print(f"{'='*80}\n")

    try:
        content = read(file_path)
        print(content)
        print(f"\n{'='*80}")
        print(f"✅ Read {len(content)} characters")
        print(f"{'='*80}\n")
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)
