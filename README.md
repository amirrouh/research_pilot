# Research Pilot

Research automation toolkit for searching academic papers, extracting text from documents, and managing research workflows.

## Features

- **Search** - PubMed, arXiv papers and NIH grants
- **OCR** - Extract text from PDFs/images with structure preservation
- **Storage** - Local database with tags and notes
- **Files** - Download, read, and write operations
- **Agents** - AI-powered automation with LangChain
- **Browser** - Web scraping and automation

## Installation

```bash
# Clone repository
git clone git@github.com:amirrouh/research_pilot.git
cd research_pilot

# Install dependencies
uv sync
```

## Quick Start

### Search Papers

```python
from assistant.tools.research.articles import query

papers = query(keywords="CRISPR", sources=[('pubmed', 5)])
print(papers[['title', 'year']])
```

### Extract Text from PDF

```python
from assistant.tools.document.ocr import read

text = read("paper.pdf")
```

### Save and Search

```python
from assistant.tools.storage.articles import save_papers_batch, search_papers_db

save_papers_batch(papers, tags=['genomics'])
saved = search_papers_db(tags=['genomics'])
```

## Configuration

Copy `config.yaml.example` to `config.yaml` and configure your LLM settings:

```yaml
llm:
  function_calling:
    model: qwen2.5:latest
    base_url: http://localhost:11434
    temperature: 0.7
```

## Documentation

View the [full documentation](https://amirrouh.github.io/research_pilot/) online.

Or build locally:
```bash
./run.sh documentation serve
```

## Project Structure

```
assistant/
├── tools/
│   ├── research/      # Search papers and grants
│   ├── document/      # OCR, read, write
│   ├── storage/       # Database operations
│   └── web/           # Download, browser automation
└── agents/            # AI agent framework
```

## License

Apache License 2.0

## Contributing

Contributions welcome. Please open an issue first to discuss changes.
