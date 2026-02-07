# Using Agents

## Search Agent

```python
from assistant.agents.core import agent
from assistant.tools.research.articles import search_papers

# Create agent
my_agent = agent(search_papers)

# Ask naturally
response = my_agent.call("Find 5 papers about CRISPR from PubMed")
print(response)
```

## Research Agent (Search + Save)

```python
from assistant.agents.core import agent
from assistant.tools.research.articles import search_papers
from assistant.tools.storage.articles import save_papers_to_db, find_saved_papers

# Create agent with multiple tools
research_agent = agent(search_papers, save_papers_to_db, find_saved_papers)

# Use naturally
research_agent.call("Find papers about quantum computing and save them with tag 'quantum'")
research_agent.call("What papers do I have about quantum?")
```

## Grants Agent

```python
from assistant.agents.core import agent
from assistant.tools.research.grants import search_grants, cite_grant
from assistant.tools.storage.grants import save_grants_to_db

# Create grants agent
grants_agent = agent(search_grants, save_grants_to_db, cite_grant)

# Use naturally
grants_agent.call("Find cancer immunotherapy grants from 2023 and save with tag 'immuno'")
```

## Different LLM Types

```python
# Use reasoning LLM
agent(search_papers, llm_type="reasoning")

# Use function calling LLM
agent(search_papers, llm_type="function_calling")
```

That's all you need.
