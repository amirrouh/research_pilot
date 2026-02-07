# Job Search

Search for jobs on LinkedIn and Indeed using a unified interface.

## Basic Usage

```python
from assistant.tools.career.search import search

# Search Indeed
jobs = search(
    platform="indeed",
    keywords="software engineer",
    location="San Francisco, CA",
    results_wanted=10
)

# Search LinkedIn
jobs = search(
    platform="linkedin",
    keywords="data scientist",
    location="New York, NY",
    results_wanted=10
)
```

## Results Format

```python
for job in jobs:
    print(f"{job['title']} at {job['company']}")
    print(f"Location: {job['location']}")
    print(f"Salary: ${job['salary_min']:,} - ${job['salary_max']:,}")
    print(f"Apply: {job['url']}")
```

## Remote Jobs

```python
jobs = search(
    platform="indeed",
    keywords="product manager",
    location="remote",
    results_wanted=20
)
```

## Data Fields

Each job contains:
- `title` - Job title
- `company` - Company name
- `location` - Job location
- `url` - Application URL
- `description` - Full description
- `year` - Posting year
- `job_type` - fulltime/parttime/contract
- `salary_min` - Minimum salary
- `salary_max` - Maximum salary
- `is_remote` - Remote flag
- `company_url` - Company website

## Using with Agents

```python
from assistant.agents.core import agent
from assistant.tools.career.search import search_jobs

# Create job search agent
job_agent = agent(search_jobs, llm_type="function_calling")

# Natural language
response = job_agent.call(
    "Find 10 software engineering jobs in Seattle on Indeed"
)
```

## Filter and Process

```python
# Get all jobs
all_jobs = search("indeed", "developer", "Austin, TX", results_wanted=50)

# Filter by salary
high_paying = [j for j in all_jobs if j.get('salary_min', 0) > 100000]

# Filter by type
full_time = [j for j in all_jobs if j.get('job_type') == 'fulltime']

# Remote only
remote_jobs = [j for j in all_jobs if j.get('is_remote')]
```

Fast and simple.
