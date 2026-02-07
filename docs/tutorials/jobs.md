# Job Search & Tracking

Search for jobs on LinkedIn and Indeed, save them to a database, and track your applications.

## Basic Search

```python
from trion.tools.career.search import search

# Search LinkedIn
jobs = search(
    platform="linkedin",
    keywords="software engineer",
    location="San Francisco, CA",
    results_wanted=10
)

# Search Indeed
jobs = search(
    platform="indeed",
    keywords="data scientist",
    location="New York, NY",
    results_wanted=10
)
```

## Search and Save (One Step)

```python
from trion.tools.career.search import search_and_save_jobs
from trion.agents.core import agent

# Create agent
job_agent = agent(search_and_save_jobs, llm_type="function_calling")

# Search and save with tags
result = job_agent.call(
    "Find 10 Python developer jobs in remote locations and tag them with 'python,remote'"
)
```

## Save to Database

```python
from trion.tools.career.search import search
from trion.tools.storage.career import save_jobs_batch

# 1. Search
jobs = search("linkedin", "machine learning", "Seattle, WA", 20)

# 2. Save with tags and status
save_jobs_batch(
    jobs,
    tags=['ml', 'seattle'],
    status='new',
    platform='linkedin'
)
```

## Search Saved Jobs

```python
from trion.tools.storage.career import search_jobs_db

# Search by keyword
jobs = search_jobs_db(keywords="python engineer")

# Search by location
jobs = search_jobs_db(location="San Francisco")

# Remote jobs only
remote = search_jobs_db(is_remote=True)

# By tags
jobs = search_jobs_db(tags=['priority', 'backend'])

# Combine filters
jobs = search_jobs_db(
    keywords="machine learning",
    location="remote",
    salary_min=100000,
    tags=['ml']
)
```

## Track Application Status

```python
from trion.tools.storage.career import update_job_status, load_jobs

# Load jobs with status
new_jobs = load_jobs(status='new', limit=20)
applied = load_jobs(status='applied')

# Update status
update_job_status(
    job_id=1,
    status='applied',
    add_tags=['priority'],
    notes='Applied via LinkedIn, phone screen scheduled'
)

# Update by URL
update_job_status(
    url='https://...',
    status='interviewing',
    notes='Technical interview on Friday'
)
```

## Job Statuses

Track your application progress:
- `new` - Just found
- `saved` - Saved for later
- `applied` - Application submitted
- `interviewing` - In interview process
- `offer` - Received offer
- `rejected` - Application rejected

## Database Statistics

```python
from trion.tools.storage.career import get_database_stats

stats = get_database_stats()
print(f"Total jobs: {stats['total_jobs']}")
print(f"Remote jobs: {stats['remote_jobs']}")
print(f"By status: {stats['by_status']}")
print(f"By platform: {stats['by_platform']}")
print(f"Tags: {stats['all_tags']}")
```

## Complete Agent Workflow

```python
from trion.tools.career.search import search_and_save_jobs
from trion.tools.storage.career import (
    find_saved_jobs,
    update_job,
    get_jobs_database_info
)
from trion.agents.core import agent

# Create agent with all tools
job_agent = agent(
    search_and_save_jobs,
    find_saved_jobs,
    update_job,
    get_jobs_database_info,
    llm_type="function_calling"
)

# Search and save
job_agent.call("Find 5 ML engineer jobs in Seattle, tag 'ml,seattle'")

# View saved jobs
job_agent.call("Show me all my saved jobs")

# Update status
job_agent.call("Mark job ID 3 as applied with note 'Applied via Indeed'")

# Get stats
job_agent.call("Show my job search statistics")
```

## Data Fields

Each job contains:
- `title` - Job title
- `company` - Company name
- `location` - Job location
- `url` - Application URL
- `description` - Full description
- `date_posted` - Posting date
- `job_type` - fulltime/parttime/contract
- `salary_min` - Minimum salary
- `salary_max` - Maximum salary
- `salary_currency` - Currency code
- `is_remote` - Remote flag
- `company_url` - Company website
- `platform` - Source platform
- `tags` - Custom tags
- `notes` - Custom notes
- `status` - Application status

## Remote Jobs

```python
# Search remote jobs
jobs = search("linkedin", "product manager", "remote", 20)

# Find saved remote jobs
remote = search_jobs_db(is_remote=True)
```

## Database Location

Configure in `config.yaml`:

```yaml
storage:
  jobs_database_path: "files/dbs/jobs.db"
```

Default: `files/dbs/jobs.db`
