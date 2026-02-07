# NIH Grants Research

Search and manage NIH grant proposals using the RePORTER API.

## Basic Search

```python
from trion.tools.research.grants import query

# Search by keywords
grants = query(keywords="cancer immunotherapy", limit=10)
```

## Filters

```python
# By PI name
grants = query(pi_name="Smith", limit=10)

# By fiscal year
grants = query(keywords="CRISPR", fiscal_years=[2023, 2024])

# By funding amount
grants = query(
    keywords="genomics",
    award_amount_min=1000000,
    limit=20
)

# Multiple filters
grants = query(
    keywords="diabetes",
    agencies=["NIDDK"],
    fiscal_years=[2023, 2024],
    award_amount_min=500000
)
```

## Save to Database

```python
from trion.tools.storage.grants import save_grants_batch

# Save with tags
save_grants_batch(grants, tags=['genomics', 'important'])
```

## Search Local Database

```python
from trion.tools.storage.grants import search_grants_db

# Search saved grants
results = search_grants_db(keywords="gene editing")

# Filter by tags
results = search_grants_db(tags=['genomics'])
```

## Generate Citations

```python
from trion.tools.research.grants import format_citation

# APA format
citation = format_citation(grants.iloc[0], style='APA')

# Vancouver format
citation = format_citation(grants.iloc[0], style='Vancouver')

# Bibtex format
citation = format_citation(grants.iloc[0], style='Bibtex')
```

## PI Portfolio

```python
from trion.tools.research.grants import get_pi_portfolio

# Get all grants for a PI
portfolio = get_pi_portfolio("John Smith")
print(f"Total funding: ${portfolio['award_amount'].sum():,}")
```

## With Agent

**Note**: Requires LLM server running (e.g., `ollama serve`).

```python
from trion.agents.core import agent
from trion.tools.research.grants import search_grants
from trion.tools.storage.grants import save_grants_to_db

# Create agent (requires LLM server running)
grants_agent = agent(search_grants, save_grants_to_db)

# Use it
grants_agent.call("Find Alzheimer's grants from 2023 and save them")
```

**Without agent** (no LLM needed):

```python
from trion.tools.research.grants import query
from trion.tools.storage.grants import save_grants_batch

# Direct function calls - always works
grants = query(keywords="Alzheimer", fiscal_years=[2023], limit=10)
save_grants_batch(grants, tags=['alzheimer', 'neuroscience'])
```

## Rate Limiting

NIH API enforces 1 request per second. Code handles this automatically.

## Database Location

Configure in `config.yaml`:

```yaml
storage:
  grants_database_path: "files/dbs/grants.db"
```
