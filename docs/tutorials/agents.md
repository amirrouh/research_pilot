# Using Agents

Two agent types available: **Basic Agents** and **DeepAgents**.

---

## Basic Agents

Simple LangChain agents for straightforward tasks.

### Search Agent

```python
from trion.agents.core import agent
from trion.tools.research.articles import search_papers

# Create agent
my_agent = agent(search_papers)

# Ask naturally
response = my_agent.call("Find 5 papers about CRISPR from PubMed")
print(response)
```

### Research Agent (Multiple Tools)

```python
from trion.agents.core import agent
from trion.tools.research.articles import search_papers
from trion.tools.storage.articles import save_papers_to_db, find_saved_papers

# Create agent with multiple tools
research_agent = agent(search_papers, save_papers_to_db, find_saved_papers)

# Use naturally
research_agent.call("Find papers about quantum computing and save them")
research_agent.call("What papers do I have about quantum?")
```

### Different LLM Types

```python
# Use reasoning LLM
agent(search_papers, llm_type="reasoning")

# Use function calling LLM
agent(search_papers, llm_type="function_calling")
```

---

## DeepAgents (Advanced)

Advanced agents with skills, planning, file access, and subagents.

**Requires Python >=3.11** (already configured in this project)

### Minimal Usage

```python
from trion.agents.deepAgent import deep_agent
from trion.tools.research.articles import search_papers

# Create agent
agent = deep_agent(search_papers)

# Use it - returns plain string
response = agent.call("Find papers about CRISPR")
print(response)
```

### With Specific Skill

```python
# Load only the "paper-finder" skill
agent = deep_agent(search_papers, skill="paper-finder")
response = agent.call("Find papers about gene therapy")
```

### With All Skills

```python
# Load all skills from ~/.trion/skills/
agent = deep_agent(search_papers, all_skills=True)
response = agent.call("Research quantum computing")
```

### Custom LLM and Prompt

```python
agent = deep_agent(
    search_papers,
    llm_type="reasoning",
    system_prompt="You are a medical research specialist"
)
response = agent.call("Find cancer research papers")
```

### Everything Combined

```python
agent = deep_agent(
    tool1,
    tool2,
    skill="paper-finder",
    llm_type="reasoning",
    system_prompt="Custom instructions"
)
response = agent.call("Your task")
```

---

## What DeepAgents Give You

- **Simple interface**: `.call(prompt)` returns plain string (no nested dicts!)
- **Skills**: Reusable capability bundles loaded by name
- **Planning**: Built-in task decomposition (write_todos tool)
- **File access**: ls, read_file, write_file, edit_file tools
- **Subagents**: Can spawn specialized agents for subtasks
- **Auto-config**: Loads from config.yaml

---

## Parameters

### Basic Agent
- `*tools` - Tools to give the agent
- `llm_type` - Which LLM config ("general", "function_calling", "reasoning")
- `system_message` - Custom instructions

### DeepAgent
- `*tools` - Tools to give the agent
- `skill` - Load specific skill by name (e.g., "paper-finder")
- `all_skills` - Load all skills from ~/.trion/skills/ (default: False)
- `llm_type` - Which LLM config ("function_calling", "reasoning", "general")
- `system_prompt` - Custom instructions

---

## Creating Skills

Skills are reusable capability bundles for DeepAgents.

See [Skills Tutorial](skills.md) for full guide.

Quick version:

1. Create `~/.trion/skills/my-skill/SKILL.md`
2. Add frontmatter + instructions:

```markdown
---
name: my-skill
description: When to use this skill
---

# My Skill

## Instructions
1. Step one
2. Step two
3. Done
```

3. Use with DeepAgent:

```python
agent = deep_agent(tool, skill="my-skill")
response = agent.call("Do something")
```

---

## Which Agent to Use?

**Use Basic Agent when:**
- Simple task with 1-3 tools
- Don't need skills or planning
- Want fast, lightweight agents

**Use DeepAgent when:**
- Need skills for reusable workflows
- Need planning/task decomposition
- Need file access built-in
- Complex multi-step tasks
- Want to spawn subagents

Both have the same `.call(prompt)` interface!
