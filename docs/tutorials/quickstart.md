# Quick Start

Get started with Trion in 5 minutes.

## Installation

```bash
pip install trion
```

## 1. Search Papers (Direct)

```python
from trion.tools.research.articles import query

# Search papers
papers = query(
    keywords="CRISPR gene editing",
    sources=[
        ('pubmed', 5),  # 5 from PubMed
        ('arxiv', 3)    # 3 from arXiv
    ]
)

# View results
print(papers[['title', 'authors', 'year']])
```

## 2. Use with Agent

```python
from trion import agent
from trion.tools.research.articles import search_papers

# Create agent
my_agent = agent(search_papers)

# Ask it to search
response = my_agent.call("Find recent papers about CRISPR gene editing")
print(response)
```

## 3. Create Custom Skill

```python
from trion import create_skill, deep_agent
from trion.tools.research.articles import search_papers

# Create skill
create_skill(
    name="literature-review",
    description="Review academic literature systematically",
    instructions="""
1. Search for papers on the specified topic
2. Extract key findings from each paper
3. Identify common themes and trends
4. Summarize the state of research
"""
)

# Use it
agent = deep_agent(search_papers, skill="literature-review")
response = agent.call("Review CRISPR papers from 2024")
print(response)
```

## 4. Create Custom Tool

```python
from trion import create_tool, agent

# Define your function
def format_citation(title: str, authors: str, year: str) -> str:
    """Format a citation in APA style"""
    return f"{authors} ({year}). {title}."

# Convert to tool
citation_tool = create_tool(
    name="format_citation",
    function=format_citation,
    description="Format academic citations in APA style"
)

# Use with agent
my_agent = agent(citation_tool)
response = my_agent.call("Format this citation: ...")
```

## 5. Discover Available Tools

```python
from trion import list_skills, list_tools, get_skill_info

# List all skills
skills = list_skills()
print(f"Built-in: {skills['built_in']}")
print(f"User: {skills['user']}")

# List all tools
tools = list_tools()
for category, tool_list in tools.items():
    print(f"{category}: {tool_list}")

# Get skill details
info = get_skill_info("paper-finder")
print(info['description'])
```

## Configuration (Optional)

Create `config.yaml` in your project or `~/.trion/config.yaml`:

```yaml
llm:
  general:
    model: qwen2.5:latest
    base_url: http://localhost:11434
    temperature: 0.7
```

## Next Steps

- [Management Functions](management.md) - Deep dive into programmatic control
- [Using Agents](agents.md) - Advanced agent patterns
- [Creating Skills](skills.md) - Build reusable capabilities
- [Searching Papers](articles.md) - Master paper search
- [Common Workflows](workflows.md) - Real-world examples

That's it! You're ready to use Trion. 🎉
