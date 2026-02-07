# Research Pilot - Code Organization Guide

## Core Principles (CRITICAL - Follow at ALL times)

1. **Temporary files**: All temporary scripts/files ONLY in `tmp/` directory
2. **Brief responses**: When answering questions, be concise - only mention important points
3. **ADHD/OCD friendly**: Keep project minimal, clean, organized - no clutter, no confusion
4. **Main code location**: All main code in `assistant/` subdirectories (assistant/tools, assistant/agents)
5. **Root directory**: ONLY CLAUDE.md and README.md allowed in project root - no other markdown files
6. **Always test**: Test modifications before marking task complete
7. **Avoid file versioning**: Modify existing files instead of creating versioned copies (no file_v2.py, file_new.py)
8. **Use subagents**: Use related subagents for important tasks to preserve context window
9. **Package manager**: Use `uv` for all Python environment management
10. **Installation**: Package installable with `uv sync` - imports work anywhere after installation
11. **No prints**: Use comprehensive logging system. If function must show output, add `verbose` argument
12. **ONE FILE = ONE PURPOSE**: NEVER create separate wrapper files. Everything for one feature goes in ONE file. No langchain_tools.py alongside articles.py. This is CRITICAL for clarity.
13. When creating test files in tmp make sure to not create multiple files for each test. as much as possible try to modify the exising related test file. also keep the files minimal.

---

## Project Structure

```
assistant/
├── config.yaml              # Configuration (gitignored)
├── config.yaml.example      # Configuration template
├── pyproject.toml          # Package definition
├── tmp/                    # Temporary files ONLY
├── assistant/              # Main package
│   ├── tools/             # All tools organized by category
│   │   └── research/
│   │       └── articles.py    # Research tool (query + LangChain tool)
│   ├── agents/            # Agent utilities
│   │   ├── core.py        # Basic agents
│   │   └── deepAgent.py   # Advanced agents with skills
│   └── skills/            # DeepAgent skills
│       └── paper-finder/
│           └── SKILL.md   # Skill definition
```

---

## Configuration System

**File**: `config.yaml` (create from `config.yaml.example`)

**Available LLM Types**:
- `function_calling`: For agents with tools/function calling
- `reasoning`: For complex reasoning tasks (lower temperature)
- `general`: For general chat/questions (DEFAULT)
- `vision`: For vision/image tasks
- `embedding`: For embeddings/semantic search

**Structure** (flat and simple):
```yaml
llm:
  function_calling:
    model: qwen2.5:latest
    base_url: http://192.168.1.92:11434
    temperature: 0.7

  reasoning:
    model: qwen3:latest
    base_url: http://192.168.1.92:11434
    temperature: 0.3
```

**To change LLM provider**: Just update the values (model, base_url, api_key if needed)
**To switch models**: Just change the model name in config.yaml

---

## How to Use Tools

### Import and Use Directly
```python
from assistant.tools.research.articles import query

# Direct function call
results = query(
    keywords="CRISPR gene editing",
    sources=[('pubmed', 5), ('arxiv', 3)]
)
```

### Use with Agent (LangChain Tool)
```python
from assistant.agents.core import agent
from assistant.tools.research.articles import search_papers

# Create agent with tool
my_agent = agent(search_papers)

# Call agent
response = my_agent.call("Find recent papers about CRISPR")
print(response)
```

---

## How to Use Agents

### Basic Pattern (Minimal and Clean)
```python
from assistant.agents.core import agent
from assistant.tools.research.articles import search_papers

# Create agent with tool(s)
my_agent = agent(search_papers)

# Call agent with prompt
response = my_agent.call("Your prompt here")
```

### Multiple Tools
```python
my_agent = agent(tool1, tool2, tool3)
response = my_agent.call("Do something")
```

### Specify LLM Type
```python
# Use reasoning LLM
my_agent = agent(search_papers, llm_type="reasoning")

# Use function calling LLM
my_agent = agent(tool1, tool2, llm_type="function_calling")
```

### Custom System Message
```python
my_agent = agent(
    search_papers,
    llm_type="general",
    system_message="You are a research assistant specialized in medical literature."
)
```

---

## How to Use DeepAgents (Advanced)

DeepAgents are advanced agents with skills, planning, file access, and subagents. **Requires Python >=3.11** (already configured).

### Quick Start (Minimal)
```python
from assistant.agents.deepAgent import deep_agent
from assistant.tools.research.articles import search_papers

# Create agent
agent = deep_agent(search_papers)

# Use it - returns plain string
response = agent.call("Find papers about CRISPR")
print(response)  # No nested dicts!
```

### With Specific Skill
```python
# Load only the "paper-finder" skill
agent = deep_agent(search_papers, skill="paper-finder")
response = agent.call("Find papers")
```

### With All Skills
```python
# Load all skills from assistant/skills/
agent = deep_agent(search_papers, all_skills=True)
response = agent.call("Research something")
```

### All Options
```python
agent = deep_agent(
    tool1, tool2,               # Tools
    skill="paper-finder",       # Specific skill
    llm_type="reasoning",       # LLM from config
    system_prompt="Custom..."   # Instructions
)

response = agent.call("Your prompt")
```

### What You Get
- **Simple interface**: `.call(prompt)` returns string
- **Skills**: Load by name (`skill="my-skill"`)
- **Planning**: Built-in task decomposition (write_todos tool)
- **File access**: ls, read_file, write_file, edit_file tools
- **Subagents**: Can spawn specialized agents
- **Auto-config**: Loads from config.yaml

### Creating Skills

Skills live in `assistant/skills/`. See `assistant/skills/README.md` for details.

Quick version:
1. Create `assistant/skills/my-skill/SKILL.md`
2. Add frontmatter + instructions
3. Use with `deep_agent(tool, skill="my-skill")`

**Example skill** (`assistant/skills/paper-finder/SKILL.md`):
```markdown
---
name: paper-finder
description: Use when user wants to search for academic papers
---

# Paper Finder

## Instructions
1. Use search_papers tool
2. Display results
3. Ask if user needs more
```

See `assistant/agents/README.md` for comprehensive guide.

---

## How to Add/Remove/Modify Components

### Adding a New Tool

1. **Choose category**: Determine which subdirectory (e.g., `assistant/tools/web/`, `assistant/tools/data/`)
2. **Create ONE file**: All logic for this tool in ONE file (no separate wrappers)
3. **Implement both**:
   - Raw function (for direct use)
   - LangChain @tool wrapper (for agents)

**Example** (`assistant/tools/web/search.py`):
```python
from langchain.tools import tool

def search_web(query: str, num_results: int = 5) -> list:
    """Direct function - implement your logic here"""
    # Your implementation
    return results

@tool
def web_search(query: str, num_results: int = 5) -> str:
    """
    LangChain tool wrapper.

    IMPORTANT: Describe when to use this tool clearly.
    """
    results = search_web(query, num_results)
    # Format results for LLM
    return formatted_results
```

### Modifying Existing Tool

1. **Find the file**: Navigate to `assistant/tools/{category}/{tool}.py`
2. **Edit in place**: Modify the existing file - do NOT create versioned copies
3. **Test**: Run tests before completing

### Removing a Tool

1. **Delete the file**: Remove `assistant/tools/{category}/{tool}.py`
2. **Check imports**: Search codebase for imports of this tool
3. **Update examples**: Remove from any example scripts in `tmp/`

### Adding New Agent Pattern

**Don't**. The `agent()` function in `assistant/agents/core.py` is the standard pattern. If you need different behavior, modify `core.py` instead of creating alternative patterns.

### Modifying Agent Behavior

**File**: `assistant/agents/core.py`

The `_Agent` class has:
- `__init__`: Setup (don't modify unless necessary)
- `call()`: Execution logic (modify for conversation history, tool execution changes, etc.)

The `agent()` function:
- Takes tools and creates agent
- Loads LLM config from YAML
- Returns `_Agent` instance

### Adding New LLM Type

1. **Edit config.yaml**:
```yaml
llm:
  your_new_type:
    model: model-name
    base_url: http://...
    temperature: 0.7
```

2. **Use it**:
```python
my_agent = agent(tool, llm_type="your_new_type")
```

---

## Testing Your Changes

### Create test script in tmp/
```python
# tmp/test_my_changes.py
from assistant.agents.core import agent
from assistant.tools.research.articles import search_papers

my_agent = agent(search_papers)
response = my_agent.call("Test query")
print(response)
```

### Run from project root
```bash
uv run tmp/test_my_changes.py
```

### Clean up after testing
Delete or keep test script in `tmp/` (not tracked by git)

---

## Project Runner Script (run.sh)

The `run.sh` script in project root provides clean, organized commands for common tasks.

### Current Commands

```bash
./run.sh documentation build    # Build docs to files/outputs/documentation_website
./run.sh documentation serve    # Start docs dev server
./run.sh help                   # Show help
```

### Adding New Commands

When adding functionality that needs a CLI command, add it to `run.sh`:

1. **Add case statement** for your new command
2. **Keep it simple** - one command, one action
3. **Add to help** - update the help section
4. **Test it** - run `./run.sh help` to verify

**Example** (adding a "test" command):
```bash
case "$1" in
    test)
        echo -e "${BLUE}Running tests...${NC}"
        uv run pytest
        echo -e "${GREEN}✓ Tests complete${NC}"
        ;;

    # ... existing commands ...

    help|--help|-h|"")
        echo "  ./run.sh test                   Run all tests"
        # ... rest of help ...
        ;;
esac
```

**Rules**:
- Keep output clean and minimal (ADHD-friendly)
- Use colors: `${BLUE}` for info, `${GREEN}` for success
- Always show what's happening
- Add every new command to help output

---

## Quick Reference

**Install package**: `uv sync`
**Run script**: `uv run script.py`
**Test changes**: Create script in `tmp/`, run with `uv run`
**Agent pattern**: `agent(tool1, tool2).call("prompt")`
**Default LLM**: `general` (unless specified with `llm_type=`)
**Config location**: `config.yaml` in project root
**Build docs**: `./run.sh documentation build`
**Serve docs**: `./run.sh documentation serve`
**See all commands**: `./run.sh help`

---

## Documentation

### Rules (CRITICAL)

1. **Only add docs when explicitly asked** - Don't create documentation proactively
2. **Follow existing style** - Minimal, concise, clear examples (see `docs/tutorials/*.md`)
3. **Location**: All docs in `docs/` folder only

### Documentation Style

- **Minimal code snippets** - Show only what's needed
- **Brief explanations** - No walls of text
- **Working examples** - Code that actually runs
- **ADHD-friendly** - Short, scannable, clear sections

**Example** (GOOD):
```markdown
# Feature Name

## Basic Use

```python
from module import function
result = function(param="value")
```

## Common Pattern

```python
# Do thing A
code_here()

# Do thing B
more_code()
```

Done.
```

**Example** (BAD):
- Long paragraphs explaining theory
- Complex examples mixing multiple concepts
- Walls of code without clear sections

### Serving Documentation

```bash
# Start live preview
uv run mkdocs serve

# Build static site
uv run mkdocs build
```

Documentation auto-refreshes when you edit Markdown files in `docs/`.
