# Searching Papers

## Basic Search

```python
from assistant.tools.research.articles import query

# Search both sources
papers = query(keywords="CRISPR")
```

## Choose Sources

```python
# Only PubMed (medical/bio)
papers = query(keywords="cancer", sources=[('pubmed', 5)])

# Only arXiv (CS/AI/physics)
papers = query(keywords="neural networks", sources=[('arxiv', 5)])

# Custom amounts
papers = query(keywords="genomics", sources=[('pubmed', 10), ('arxiv', 3)])
```

## Recent Papers Only

```python
# Last 2 years
papers = query(keywords="COVID-19", recent_years=2)
```

## View Results

```python
# See what you got
print(papers[['title', 'year', 'source']])

# Access a paper
first = papers.iloc[0]
print(first['title'])
print(first['abstract'])
print(first['url'])
```

That's it.
