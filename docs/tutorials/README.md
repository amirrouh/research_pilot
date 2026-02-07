# Installation & Setup

Get Trion up and running in minutes.

## Installation

### Basic Installation

```bash
pip install trion[all]
```

This installs Trion with all features enabled.

### Feature-Specific Installation

Install only what you need:

```bash
# Research tools only
pip install trion[research]

# Document processing
pip install trion[document]

# Web automation
pip install trion[web]

# Development tools
pip install trion[dev]
```

### Development Installation

If you're developing or contributing:

```bash
git clone https://github.com/yourusername/trion.git
cd trion
pip install -e .[all]
```

## Configuration (Optional)

Trion works out of the box, but you can customize LLM settings.

### Create Config File

Create `config.yaml` in your project directory or `~/.trion/config.yaml`:

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

### Config Priority

Trion searches for config in this order:
1. Current directory (`./config.yaml`)
2. Parent directories (walking up the tree)
3. User home (`~/.trion/config.yaml`)
4. Built-in defaults

## Quick Test

Verify installation:

```python
# Test imports
from trion import agent, deep_agent, create_skill, create_tool

# Test research tools
from trion.tools.research.articles import query

# Search papers (no LLM needed)
papers = query(keywords="machine learning", sources=[('arxiv', 3)])
print(f"Found {len(papers)} papers")

# List available tools
from trion import list_tools, list_skills

tools = list_tools()
print(f"Tool categories: {list(tools.keys())}")

skills = list_skills()
print(f"Built-in skills: {skills['built_in']}")
```

## Quick Example

```python
from trion.tools.research.articles import query
from trion.tools.storage.articles import save_papers_batch, search_papers_db

# Search papers
papers = query(keywords="CRISPR", sources=[('pubmed', 5)])

# Save them
save_papers_batch(papers, tags=['genomics'])

# Find later
saved = search_papers_db(tags=['genomics'])
print(f"Saved papers: {len(saved)}")
```

## Next Steps

1. [Quick Start](quickstart.md) - 5-minute tutorial
2. [Management Functions](management.md) - Create skills and tools
3. [Searching Papers](articles.md) - Deep dive into paper search
4. [Using Agents](agents.md) - AI-powered workflows

## Troubleshooting

### Import Errors

If you get `ModuleNotFoundError`:

```bash
# Make sure trion is installed
pip show trion

# Reinstall if needed
pip install --upgrade trion[all]
```

### Autocomplete Not Working

See [autocomplete fix guide](../../tmp/AUTOCOMPLETE_FIX.md) for IDE setup.

### LLM Connection Issues

If agents fail to connect:

1. Check LLM server is running (e.g., Ollama at `http://localhost:11434`)
2. Verify `config.yaml` has correct `base_url`
3. Test connection: `curl http://localhost:11434/api/tags`

### Database Issues

If storage tools fail:

```bash
# Check database location
ls -la files/dbs/

# Create directory if needed
mkdir -p files/dbs
```

## Requirements

- **Python**: >= 3.11
- **Operating System**: macOS, Linux, Windows
- **LLM Server** (optional): Ollama, OpenAI API, or compatible

That's it! You're ready to go. 🚀
