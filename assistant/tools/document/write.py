"""
File Write Tool - Write files to disk

Simple interface to write text files.

Usage:
    from assistant.tools.document.write import write

    # Write file
    write("Hello world", "output.txt")

Returns:
    str: Path to written file
"""

from typing import Union
from pathlib import Path


def write(
    content: str,
    file_path: Union[str, Path],
    encoding: str = "utf-8"
) -> str:
    """
    Write content to a text file.

    Args:
        content: Text content to write
        file_path: Path to save the file (including extension)
        encoding: File encoding (default: utf-8)

    Returns:
        Absolute path to the written file

    Examples:
        write("# Title\n\nContent", "document.md")
        write('{"key": "value"}', "data.json")
        write("Hello", "output.txt")
    """
    file_path = Path(file_path)

    # Create parent directory if it doesn't exist
    file_path.parent.mkdir(parents=True, exist_ok=True)

    # Write file
    with open(file_path, 'w', encoding=encoding) as f:
        f.write(content)

    return str(file_path.absolute())


# LangChain Tool Wrapper
try:
    from langchain_core.tools import tool

    @tool
    def write_file(content: str, file_path: str) -> str:
        """
        Write text content to a file.

        Use this tool when you need to:
        - Save text to files
        - Create documents, notes, or data files
        - Export content to disk

        Supports: txt, md, json, csv, xml, html, py, etc.

        Args:
            content: Text content to write
            file_path: Path where to save (e.g., "output.txt", "data.json")

        Returns:
            Absolute path to the written file
        """
        result = write(content, file_path)
        return f"Written to: {result}"

except ImportError:
    # LangChain not installed - skip tool creation
    pass


# Test
if __name__ == "__main__":
    import sys

    if len(sys.argv) < 3:
        print("Usage: python write.py <file_path> <content>")
        print("\nExample:")
        print("  python write.py output.txt 'Hello world'")
        sys.exit(1)

    file_path = sys.argv[1]
    content = sys.argv[2]

    print(f"\n{'='*80}")
    print(f"Writing to: {file_path}")
    print(f"Content length: {len(content)} characters")
    print(f"{'='*80}\n")

    try:
        result = write(content, file_path)
        print(f"✅ Written successfully!")
        print(f"Location: {result}")
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)

    print(f"\n{'='*80}\n")
