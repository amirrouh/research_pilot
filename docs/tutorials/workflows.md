# Common Workflows

## 1. Build Reading List

```python
from assistant.tools.research.articles import query
from assistant.tools.storage.articles import save_papers_batch

papers = query(keywords="machine learning", sources=[('arxiv', 10)])
save_papers_batch(papers, tags=['ml', 'to-read'])
```

## 2. Organize by Project

```python
from assistant.tools.storage.articles import search_papers_db, tag_paper

# Get papers
papers = search_papers_db(keywords="genomics")

# Tag for project
for _, paper in papers.iterrows():
    paper_id = paper['pmid'] if paper['pmid'] != 'N/A' else paper.get('arxiv_id')
    if paper_id and paper_id != 'N/A':
        tag_paper(paper_id, add_tags=['project-a'])
```

## 3. Literature Review

```python
# Search and categorize
sections = {
    'background': "CRISPR history",
    'methods': "CRISPR techniques",
    'results': "CRISPR clinical trials"
}

for section, keywords in sections.items():
    papers = query(keywords=keywords, sources=[('pubmed', 5)])
    save_papers_batch(papers, tags=['lit-review', section])
```

## 4. Find Papers to Cite

```python
# Mark important papers
tag_paper("12345678", add_tags=['cite-in-paper'], notes="Use in introduction")

# Find all papers to cite
to_cite = search_papers_db(tags=['cite-in-paper'])
print(to_cite[['title', 'authors', 'year']])
```

## 5. Grant Research

```python
from assistant.tools.research.grants import query, format_citation
from assistant.tools.storage.grants import save_grants_batch

# Search grants
grants = query(keywords="cancer immunotherapy", fiscal_years=[2023, 2024])

# Save high-value grants
high_value = grants[grants['award_amount'] > 5000000]
save_grants_batch(high_value, tags=['immunotherapy', 'high-value'])

# Generate citations
for _, grant in high_value.head(3).iterrows():
    print(format_citation(grant, style='APA'))
```

## 6. PI Analysis

```python
from assistant.tools.research.grants import get_pi_portfolio

# Get PI's funding history
portfolio = get_pi_portfolio("John Smith")

# Analyze
total = portfolio['award_amount'].sum()
by_year = portfolio.groupby('fiscal_year')['award_amount'].sum()

print(f"Total funding: ${total:,}")
print(f"By year:\n{by_year}")
```

## 7. Extract Text from PDFs

```python
from assistant.tools.document.ocr import read

# Extract from research paper
text = read("paper.pdf")

# Process specific page
page1 = read("paper.pdf", page=1)

# Extract from scanned document
scanned = read("scanned_form.jpg")
```

## 8. OCR with Agent

```python
from assistant.agents.core import agent
from assistant.tools.document.ocr import ocr_read

# Create OCR agent
ocr_agent = agent(ocr_read, llm_type="function_calling")

# Natural language processing
response = ocr_agent.call("Extract the abstract from paper.pdf page 1")
```

Simple.
