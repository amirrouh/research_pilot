# Tutorials

Quick guides for common tasks.

## Start Here

1. **[Searching Papers](articles.md)** - Find papers from PubMed/arXiv
2. **[Google Scholar](google_scholar.md)** - Scrape author profiles and publications
3. **[Job Search](jobs.md)** - Search LinkedIn and Indeed
4. **[Document OCR](ocr.md)** - Extract text from PDFs/images
5. **[File Operations](files.md)** - Download, read, write files
6. **[Saving & Finding](storage.md)** - Save papers, search later
7. **[NIH Grants](grants.md)** - Search and manage NIH grants
8. **[Using Agents](agents.md)** - Let AI do the work
9. **[Creating Skills](skills.md)** - Reusable agent workflows
10. **[Browser Tool](browser.md)** - Web automation
11. **[Common Workflows](workflows.md)** - Real examples

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
