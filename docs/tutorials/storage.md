# Saving & Finding Papers

## Save Papers

```python
from assistant.tools.research.articles import query
from assistant.tools.storage.articles import save_papers_batch

# 1. Search
papers = query(keywords="CRISPR", sources=[('pubmed', 5)])

# 2. Save with tags
save_papers_batch(papers, tags=['genomics', 'important'])
```

## Find Saved Papers

```python
from assistant.tools.storage.articles import search_papers_db

# Search by keyword
papers = search_papers_db(keywords="CRISPR")

# Search by tag
papers = search_papers_db(tags=['important'])

# Both
papers = search_papers_db(keywords="gene editing", tags=['genomics'])
```

## Add Tags Later

```python
from assistant.tools.storage.articles import tag_paper

# Add tags to a paper (use PMID or arXiv ID)
tag_paper("12345678", add_tags=['must-read', 'cite-this'])

# Add notes
tag_paper("12345678", notes="Key paper for introduction")
```

## See What You Have

```python
from assistant.tools.storage.articles import get_database_stats

stats = get_database_stats()
print(f"Total papers: {stats['total_papers']}")
print(f"Tags: {stats['tags']}")
```

Done.
