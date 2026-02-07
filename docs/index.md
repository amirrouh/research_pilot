# Research Pilot Documentation

Research automation tool for searching academic papers (PubMed, arXiv) and NIH grant proposals.

## Quick Start

```python
from assistant.tools.research.articles import query
from assistant.tools.storage.articles import save_papers_batch

# Search papers
papers = query(keywords="CRISPR", sources=[('pubmed', 5)])

# Save them
save_papers_batch(papers, tags=['genomics'])
```

## Features

- **Search** - PubMed, arXiv papers and NIH grants
- **OCR** - Extract text from PDFs/images with structure preservation
- **Files** - Download, read, and write files
- **Save** - Local SQLite database
- **Organize** - Tags and notes
- **Agents** - AI-powered research assistant

## Installation

```bash
uv sync
```

## Tutorials

Start with the [tutorials](tutorials/README.md) to learn:

- [Searching Papers](tutorials/articles.md)
- [Document OCR](tutorials/ocr.md)
- [File Operations](tutorials/files.md)
- [Saving & Finding Papers](tutorials/storage.md)
- [NIH Grants](tutorials/grants.md)
- [Using Agents](tutorials/agents.md)
- [Browser Tool](tutorials/browser.md)
- [Common Workflows](tutorials/workflows.md)

## Project Structure

```
assistant/
├── tools/
│   ├── research/      # Search tools (articles, grants)
│   ├── document/      # OCR and document processing
│   ├── storage/       # Database tools
│   └── web/           # Browser automation
└── agents/            # AI agents
```

Simple.
