# Google Scholar

Scrape complete Google Scholar profiles with all publications and author metrics.

## Basic Usage

```python
from trion.tools.research.google_scholar import fetch_profile

# Scrape profile
result = fetch_profile(
    "https://scholar.google.com/citations?user=JicYPdAAAAAJ&hl=en"
)

# Access author info
author = result['author']
print(f"{author['name']} - {author['affiliation']}")
print(f"Citations: {author['total_citations']:,}")
print(f"h-index: {author['h_index']}")

# Access publications
for pub in result['publications']:
    print(f"{pub['title']} - {pub['citations']} citations")
```

## Author Fields

```python
author = result['author']
# name, affiliation, scholar_id, profile_url
# total_citations, h_index, i10_index
# email_domain
```

## Publication Fields

```python
pub = result['publications'][0]
# title, authors, venue, year, citations
# scholar_url
```

## Filter Publications

```python
result = fetch_profile(profile_url)

# Highly cited papers
highly_cited = [
    p for p in result['publications']
    if p.get('citations', 0) > 10000
]

# Recent papers
recent = [
    p for p in result['publications']
    if p.get('year', 0) >= 2020
]

# Sort by citations
sorted_pubs = sorted(
    result['publications'],
    key=lambda p: p.get('citations', 0),
    reverse=True
)
```

## Pagination Control

```python
# Limit pages for faster scraping
result = fetch_profile(
    profile_url,
    max_pages=5,  # Stop after 5 pages (~500 pubs)
    verbose=True   # Show progress
)
```

## Save Results

```python
import json

result = fetch_profile(profile_url)

# Save as JSON
with open('author.json', 'w') as f:
    json.dump(result, f, indent=2)

# Or use pandas
import pandas as pd
df = pd.DataFrame(result['publications'])
df.to_csv('publications.csv', index=False)
```

## Using with Agents

```python
from trion.agents.core import agent
from trion.tools.research.google_scholar import scrape_scholar_profile

# Create scholar agent
scholar_agent = agent(scrape_scholar_profile, llm_type="function_calling")

# Natural language
response = scholar_agent.call(
    "Scrape Yann LeCun's profile and show his top papers: "
    "https://scholar.google.com/citations?user=WLN3QrAAAAAJ&hl=en"
)
```

## Performance

- ~2-3 seconds per page
- 100 publications per page
- 2-second delay between pages
- Max 50 pages (5000 publications)

Comprehensive and reliable.
