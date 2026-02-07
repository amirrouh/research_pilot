# Storage & Databases

Save and manage papers, grants, and job applications in local SQLite databases.

## Papers

### Save Papers

```python
from trion.tools.research.articles import query
from trion.tools.storage.articles import save_papers_batch

# 1. Search
papers = query(keywords="CRISPR", sources=[('pubmed', 5)])

# 2. Save with tags
save_papers_batch(papers, tags=['genomics', 'important'])
```

### Find Saved Papers

```python
from trion.tools.storage.articles import search_papers_db

# Search by keyword
papers = search_papers_db(keywords="CRISPR")

# Search by tag
papers = search_papers_db(tags=['important'])

# Both
papers = search_papers_db(keywords="gene editing", tags=['genomics'])
```

### Add Tags

```python
from trion.tools.storage.articles import tag_paper

# Add tags to a paper (use PMID or arXiv ID)
tag_paper("12345678", add_tags=['must-read', 'cite-this'])

# Add notes
tag_paper("12345678", notes="Key paper for introduction")
```

## Grants

### Save Grants

```python
from trion.tools.research.grants import query
from trion.tools.storage.grants import save_grants_batch

# 1. Search
grants = query(keywords="cancer", fiscal_years=[2024], limit=10)

# 2. Save with tags
save_grants_batch(grants, tags=['cancer', 'important'])
```

### Find Saved Grants

```python
from trion.tools.storage.grants import search_grants_db

# Search by keyword
grants = search_grants_db(keywords="immunotherapy")

# Search by tag
grants = search_grants_db(tags=['cancer'])

# Filter by fiscal year
grants = search_grants_db(fiscal_year_from=2020, fiscal_year_to=2024)
```

## Jobs

### Save Jobs

```python
from trion.tools.career.search import search
from trion.tools.storage.career import save_jobs_batch

# 1. Search
jobs = search("linkedin", "software engineer", "San Francisco, CA", 10)

# 2. Save with tags and status
save_jobs_batch(
    jobs,
    tags=['python', 'backend'],
    status='new',
    platform='linkedin'
)
```

### Find Saved Jobs

```python
from trion.tools.storage.career import search_jobs_db

# Search by keyword
jobs = search_jobs_db(keywords="python engineer")

# Search by location
jobs = search_jobs_db(location="San Francisco")

# Remote jobs only
remote = search_jobs_db(is_remote=True)

# By tags and salary
jobs = search_jobs_db(tags=['priority'], salary_min=100000)
```

### Track Applications

```python
from trion.tools.storage.career import update_job_status

# Update status
update_job_status(
    job_id=1,
    status='applied',
    add_tags=['priority'],
    notes='Applied via LinkedIn'
)

# Track progress
update_job_status(job_id=1, status='interviewing')
update_job_status(job_id=1, status='offer')
```

## Database Statistics

```python
# Papers
from trion.tools.storage.articles import get_database_stats
stats = get_database_stats()
print(f"Total papers: {stats['total_papers']}")

# Grants
from trion.tools.storage.grants import get_database_stats
stats = get_database_stats()
print(f"Total grants: {stats['total_grants']}")
print(f"Total funding: ${stats['total_funding']:,}")

# Jobs
from trion.tools.storage.career import get_database_stats
stats = get_database_stats()
print(f"Total jobs: {stats['total_jobs']}")
print(f"By status: {stats['by_status']}")
```

## Database Locations

Default locations (configurable in `config.yaml`):

```yaml
storage:
  papers_database_path: "files/dbs/papers.db"
  grants_database_path: "files/dbs/grants.db"
  jobs_database_path: "files/dbs/jobs.db"
```

## Search and Save in One Step

### Grants

```python
from trion.tools.research.grants import search_and_save_grants
from trion.agents.core import agent

agent = agent(search_and_save_grants, llm_type="function_calling")
agent.call("Find cancer grants from 2024 and tag them 'cancer,immunotherapy'")
```

### Jobs

```python
from trion.tools.career.search import search_and_save_jobs
from trion.agents.core import agent

agent = agent(search_and_save_jobs, llm_type="function_calling")
agent.call("Find 10 Python jobs in remote locations and tag them 'python,remote'")
```

Done.
