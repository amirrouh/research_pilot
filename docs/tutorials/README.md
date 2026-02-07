# Tutorials

Quick guides for common tasks.

## Start Here

1. **[Searching Papers](articles.md)** - Find papers from PubMed/arXiv
2. **[Document OCR](ocr.md)** - Extract text from PDFs/images
3. **[File Operations](files.md)** - Download, read, write files
4. **[Saving & Finding](storage.md)** - Save papers, search later
5. **[NIH Grants](grants.md)** - Search and manage NIH grants
6. **[Using Agents](agents.md)** - Let AI do the work
7. **[Browser Tool](browser.md)** - Web automation
8. **[Common Workflows](workflows.md)** - Real examples

## Quick Example

```python
from assistant.tools.research.articles import query
from assistant.tools.storage.articles import save_papers_batch, search_papers_db

# Search
papers = query(keywords="CRISPR", sources=[('pubmed', 5)])

# Save
save_papers_batch(papers, tags=['genomics'])

# Find later
saved = search_papers_db(tags=['genomics'])
```

That's it.
