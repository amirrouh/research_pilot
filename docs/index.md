# Trion Documentation

**Transdisciplinary Research Intelligence & Opportunity Navigation**

Pure Python library for research automation, academic literature search, document processing, and intelligent agents.

## Quick Start

```python
# Install
pip install trion[all]

# Search papers
from trion.tools.research.articles import query
papers = query(keywords="CRISPR", sources=[('pubmed', 5)])

# Use with agent
from trion import agent
from trion.tools.research.articles import search_papers

my_agent = agent(search_papers)
response = my_agent.call("Find recent CRISPR papers")
```

## Key Features

- **Pure Library** - No CLI, just import and use
- **Research Tools** - Search PubMed, arXiv, Google Scholar, NIH grants
- **Document Processing** - OCR, PDF extraction with structure preservation
- **Web Automation** - Browser automation with Playwright
- **Agent Framework** - Basic and advanced agents (DeepAgents) with tools
- **Skills System** - Reusable capability bundles for agents
- **Programmatic Management** - Create skills and tools with simple functions

## Installation

### Basic Installation

```bash
pip install trion[all]
```

### Feature-Specific Installation

```bash
pip install trion[research]  # Research tools only
pip install trion[document]  # Document processing
pip install trion[web]       # Web automation
pip install trion[dev]       # Development tools
```

## Core Concepts

### 1. Direct Tool Usage

Import and use tools directly:

```python
from trion.tools.research.articles import query

papers = query(
    keywords="machine learning",
    sources=[('arxiv', 10)]
)
```

### 2. Agent Framework

Use tools with AI agents:

```python
from trion import agent
from trion.tools.research.articles import search_papers

my_agent = agent(search_papers)
response = my_agent.call("Find papers about transformers")
```

### 3. Skills System

Create reusable capability bundles:

```python
from trion import create_skill, deep_agent
from trion.tools.research.articles import search_papers

# Create skill
create_skill(
    name="literature-review",
    description="Review academic literature",
    instructions="1. Search\n2. Analyze\n3. Summarize"
)

# Use it
agent = deep_agent(search_papers, skill="literature-review")
```

### 4. Programmatic Management

Create and manage skills/tools programmatically:

```python
from trion import (
    create_skill,
    create_tool,
    list_skills,
    list_tools,
    get_skill_info
)

# Create custom tool
def my_function(query: str) -> str:
    return f"Result: {query}"

tool = create_tool(
    name="my_tool",
    function=my_function,
    description="Custom tool"
)
```

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

## Getting Started

1. [Installation Guide](tutorials/README.md) - Set up Trion
2. [Quick Start](tutorials/quickstart.md) - Get started in 5 minutes
3. [Management Functions](tutorials/management.md) - Create skills and tools
4. [Using Agents](tutorials/agents.md) - AI-powered workflows
5. [Creating Skills](tutorials/skills.md) - Reusable capabilities

## Available Tools

### Research
- [Searching Papers](tutorials/articles.md) - PubMed and arXiv search
- [Google Scholar](tutorials/google_scholar.md) - Academic search
- [NIH Grants](tutorials/grants.md) - Grant opportunity search

### Document Processing
- [Document OCR](tutorials/ocr.md) - Extract text from images/PDFs
- [File Operations](tutorials/files.md) - Read and write documents

### Web & Automation
- [Browser Automation](tutorials/browser.md) - Playwright integration
- [Job Search](tutorials/jobs.md) - Find academic positions

### Storage
- [Storage & Database](tutorials/storage.md) - Save and retrieve papers

## Common Workflows

Check out [Common Workflows](tutorials/workflows.md) for real-world examples:

- Literature review automation
- Grant opportunity monitoring
- Job market tracking
- Research paper organization

## Philosophy

Trion is designed to be:

- **Simple** - Just import and use, no CLI complexity
- **Flexible** - Programmatic control over everything
- **Minimal** - Clean, focused functionality
- **Intuitive** - Clear, consistent API
- **Powerful** - Advanced features when you need them

## Support

- **Issues**: [GitHub Issues](https://github.com/yourusername/trion/issues)
- **Documentation**: This site
- **Source Code**: [GitHub Repository](https://github.com/yourusername/trion)
