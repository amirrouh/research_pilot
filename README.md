# Research Pilot

Automate research workflows: search papers, extract text from documents, and organize findings.

## Features

- **Search** - PubMed, arXiv papers and NIH grants
- **OCR** - Extract text from PDFs/images with structure preservation
- **Storage** - Local SQLite database with tags and notes
- **Agents** - AI-powered automation with LangChain
- **Browser** - Web automation for scraping and interaction

## Quick Start

```bash
# Install
uv sync

# Search papers
uv run python -c "
from assistant.tools.research.articles import query
papers = query(keywords='CRISPR', sources=[('pubmed', 5)])
print(papers[['title', 'year']])
"

# Extract text from PDF
uv run python -c "
from assistant.tools.document.ocr import read
text = read('document.pdf')
print(text[:500])
"
```

## Documentation

Full documentation: `./run.sh documentation serve`

Or see [docs/](docs/index.md)

## Project Structure

```
assistant/
├── tools/
│   ├── research/      # Search papers and grants
│   ├── document/      # OCR and document processing
│   ├── storage/       # Database operations
│   └── web/           # Browser automation
└── agents/            # AI agent framework
```

## Configuration

Copy `config.yaml.example` to `config.yaml` and configure LLM settings:

```yaml
llm:
  function_calling:
    model: qwen2.5:latest
    base_url: http://localhost:11434
```

## Development

See [CLAUDE.md](CLAUDE.md) for code organization rules and development guidelines.

## License

Private project.
