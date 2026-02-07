# Agents

Two agent types available:

1. **Basic agents** (`core.py`) - Simple LangChain agents
2. **DeepAgents** (`deepAgent.py`) - Advanced agents with skills, planning, file access

---

## DeepAgent (Recommended)

**Location**: `assistant/agents/deepAgent.py`

### Quick Start

```python
from assistant.agents.deepAgent import deep_agent
from assistant.tools.research.articles import search_papers

# Create and use
agent = deep_agent(search_papers)
response = agent.call("Find papers about CRISPR")
print(response)  # Plain string, no nested dicts
```

### All Options

```python
agent = deep_agent(
    tool1, tool2,           # Tools
    skill="paper-finder",   # Load specific skill
    llm_type="reasoning",   # LLM type from config
    system_prompt="..."     # Custom instructions
)

response = agent.call("Your prompt here")
```

### Parameters

- `*tools` - Tools to give the agent
- `skill` - Load specific skill by name (e.g., `"paper-finder"`)
- `all_skills` - Load all skills from `assistant/skills/` (default: False)
- `llm_type` - Which LLM config (`"function_calling"`, `"reasoning"`, `"general"`)
- `system_prompt` - Custom instructions

### What You Get

✓ Simple `.call(prompt)` → returns string
✓ Skills loaded by name
✓ Built-in planning (write_todos tool)
✓ Built-in file access (ls, read_file, write_file, edit_file)
✓ Can spawn subagents
✓ Auto-loads config from `config.yaml`

---

## Basic Agent

**Location**: `assistant/agents/core.py`

### Quick Start

```python
from assistant.agents.core import agent
from assistant.tools.research.articles import search_papers

# Create and use
my_agent = agent(search_papers)
response = my_agent.call("Find papers about CRISPR")
print(response)
```

### All Options

```python
my_agent = agent(
    tool1, tool2,
    llm_type="reasoning",
    system_message="Custom instructions"
)

response = my_agent.call("Your prompt")
```

### When to Use

Use basic agents when you:
- Don't need skills
- Don't need planning or file access
- Want simpler, faster agents

---

## Skills

**Location**: `assistant/skills/`

See `assistant/skills/README.md` for creating skills.

Quick version:
1. Create `assistant/skills/my-skill/SKILL.md`
2. Add frontmatter + instructions
3. Use with `deep_agent(tool, skill="my-skill")`

---

## Examples

Both agent types have the same `.call(prompt)` interface:

```python
# DeepAgent
from assistant.agents.deepAgent import deep_agent
agent = deep_agent(tool)
response = agent.call("prompt")

# Basic agent
from assistant.agents.core import agent
my_agent = agent(tool)
response = my_agent.call("prompt")
```

Choose DeepAgent for advanced features, basic agent for simplicity.
