# Document OCR

Extract text from PDFs and images with structure preservation using Docling (IBM Research).

## Basic Usage

```python
from trion.tools.document.ocr import read

# Extract from PDF
text = read("document.pdf")

# Extract from image
text = read("scan.jpg")
```

## Single Page

```python
# Extract specific page
text = read("paper.pdf", page=1)
```

## What It Preserves

- **Tables** - Proper markdown tables
- **Headings** - Section hierarchy
- **Lists** - Bullet and numbered
- **Paragraphs** - Reading order
- **Code blocks** - Syntax preserved

## Output Format

Clean Markdown:

```markdown
## Section Title

This is a paragraph with proper formatting.

- Bullet point 1
- Bullet point 2

| Column 1 | Column 2 |
|----------|----------|
| Data     | Data     |
```

## Supported Formats

- **PDF** - Multi-page documents
- **Images** - JPG, PNG
- **Office** - DOCX, PPTX, XLSX
- **Web** - HTML
- **eBooks** - EPUB

## Using with Agents

```python
from trion.agents.core import agent
from trion.tools.document.ocr import ocr_read

# Create OCR agent
ocr_agent = agent(ocr_read, llm_type="function_calling")

# Natural language
response = ocr_agent.call("Read the text from document.pdf")
```

Simple and accurate.
