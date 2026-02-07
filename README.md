# Trion

**Transdisciplinary Research Intelligence & Opportunity Navigation**

Pure Python library for research automation, academic literature search, document processing, and intelligent agents.

## Features

- **Research Tools** - Search PubMed, arXiv, Google Scholar, NIH grants
- **Document Processing** - OCR, PDF extraction with structure preservation
- **Web Automation** - Browser automation with Playwright
- **Job Search** - Indeed integration for academic positions
- **Agent Framework** - Basic and advanced agents (DeepAgents) with tools
- **Skills System** - Reusable capability bundles for agents
- **Programmatic Management** - Create skills and tools with simple functions

## Installation

```bash
pip install trion
```

That's it! All features included.

## Quick Start

### Search Papers

```python
from trion.tools.research.articles import query

papers = query(keywords="CRISPR", sources=[('pubmed', 5), ('arxiv', 3)])
print(papers[['title', 'year']])
```

### Use with Agent

```python
from trion.agents import agent
from trion.tools.research.articles import search_papers

my_agent = agent(search_papers)
response = my_agent.call("Find recent papers about CRISPR gene editing")
print(response)
```

### Use DeepAgent with Skills

```python
from trion.agents import deep_agent
from trion.tools.research.articles import search_papers

# Use built-in skill
my_agent = deep_agent(search_papers, skill="paper-finder")
response = my_agent.call("Research recent CRISPR developments")
print(response)
```

### Create Custom Skills

```python
from trion import create_skill

# From markdown file
create_skill(markdown_path="my_skill.md")

# Programmatically
create_skill(
    name="literature-review",
    description="Review academic literature",
    instructions="1. Search papers\n2. Analyze results\n3. Summarize findings"
)

# Use it
from trion.agents import deep_agent
from trion.tools.research.articles import search_papers

agent = deep_agent(search_papers, skill="literature-review")
response = agent.call("Review CRISPR papers from 2024")
```

### Create Custom Tools

```python
from trion import create_tool

def my_function(query: str) -> str:
    """My custom function"""
    return f"Result for {query}"

# Create tool
tool = create_tool(
    name="my_tool",
    function=my_function,
    description="Custom tool for specific task"
)

# Use with agent
from trion.agents import agent
my_agent = agent(tool)
response = my_agent.call("Use my custom tool")
```

### List Available Skills and Tools

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

## Configuration

Create `config.yaml` anywhere in your project tree:

```yaml
llm:
  general:
    model: qwen2.5:latest
    base_url: http://localhost:11434
    temperature: 0.7

  function_calling:
    model: qwen2.5:latest
    base_url: http://localhost:11434
    temperature: 0.7

  reasoning:
    model: qwen3:latest
    base_url: http://localhost:11434
    temperature: 0.3
```

Trion searches upward from current directory, falls back to `~/.trion/config.yaml`, or uses defaults.

## Project Structure

```
trion/
├── agents/          # Agent framework (basic and DeepAgents)
├── tools/           # Built-in tools
│   ├── research/    # Academic search (PubMed, arXiv, etc.)
│   ├── document/    # Document processing (OCR, read/write)
│   ├── web/         # Web automation and search
│   ├── storage/     # Local SQLite storage
│   └── career/      # Job search
├── skills/          # Built-in skills for DeepAgents
├── utils/           # Utilities (config loading)
└── management.py    # Programmatic skill/tool creation
```

## Available Tools

### Research Tools

```python
from trion.tools.research.articles import query, search_papers
from trion.tools.research.grants import search_grants
from trion.tools.research.google_scholar import google_scholar_search
```

### Document Tools

```python
from trion.tools.document.read import read_document
from trion.tools.document.write import write_document
from trion.tools.document.ocr import extract_text_from_image
```

### Web Tools

```python
from trion.tools.web.browser import browse_web
from trion.tools.web.download import download_file
from trion.tools.web.web_search import search_web
```

### Storage Tools

```python
from trion.tools.storage.articles import save_papers, get_papers
from trion.tools.storage.grants import save_grants, get_grants
```

## Advanced Usage

### Multiple Tools with Agent

```python
from trion.agents import agent
from trion.tools.research.articles import search_papers
from trion.tools.web.web_search import search_web

my_agent = agent(search_papers, search_web)
response = my_agent.call("Find papers and web resources about CRISPR")
```

### DeepAgent with All Skills

```python
from trion.agents import deep_agent
from trion.tools.research.articles import search_papers

# Load all available skills
agent = deep_agent(search_papers, all_skills=True)
response = agent.call("Comprehensive research task")
```

### Custom LLM Configuration

```python
from trion.agents import agent
from trion.tools.research.articles import search_papers

# Use reasoning LLM for complex tasks
agent = agent(search_papers, llm_type="reasoning")

# Use function calling LLM
agent = agent(search_papers, llm_type="function_calling")
```

### Custom System Message

```python
from trion.agents import agent
from trion.tools.research.articles import search_papers

agent = agent(
    search_papers,
    system_message="You are a medical research specialist focused on oncology."
)
```

## Development

```bash
# Clone repository
git clone <repo-url>
cd trion

# Install with all dependencies
uv sync --extra all

# Run tests
pytest
```

## License

MIT

## Documentation

For comprehensive documentation, tutorials, and API reference, visit the [documentation site](https://yourusername.github.io/trion).
