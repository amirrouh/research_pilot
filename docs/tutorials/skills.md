# Skills

Skills are reusable capability bundles for DeepAgents.

---

## What are Skills?

Skills define specialized workflows that DeepAgents can load automatically. Each skill is a directory with a `SKILL.md` file containing:

- **Frontmatter**: Metadata (name, description)
- **Instructions**: Step-by-step guidance for the agent

---

## Quick Start

### 1. Create Skill Directory

```bash
mkdir -p assistant/skills/my-skill
```

### 2. Create SKILL.md

Create `assistant/skills/my-skill/SKILL.md`:

```markdown
---
name: my-skill
description: When to use this skill (be specific)
---

# My Skill

## Overview
What this skill does

## Instructions
1. Step one
2. Step two
3. Step three

## Available Tools
- tool_name: What it does
```

### 3. Use with DeepAgent

```python
from assistant.agents.deepAgent import deep_agent
from assistant.tools.some_tool import my_tool

# Load specific skill
agent = deep_agent(my_tool, skill="my-skill")
response = agent.call("Do something")
```

---

## Example: Paper Finder Skill

**Location**: `assistant/skills/paper-finder/SKILL.md`

```markdown
---
name: paper-finder
description: Use when user wants to search for academic papers from PubMed or arXiv
---

# Paper Finder Skill

## Overview
Searches PubMed and arXiv for academic papers and presents results clearly.

## Instructions

1. Identify the research topic from the user's request
2. Use the `search_papers` tool to find relevant papers
3. Display results showing:
   - Paper title
   - Authors
   - Publication year
   - Source (PubMed/arXiv)
4. Provide clear, organized results

## Available Tools
- `search_papers`: Searches PubMed and arXiv databases
```

**Usage**:

```python
from assistant.agents.deepAgent import deep_agent
from assistant.tools.research.articles import search_papers

agent = deep_agent(search_papers, skill="paper-finder")
response = agent.call("Find CRISPR papers")
print(response)
```

---

## Frontmatter Fields

### Required

- `description` - When to use this skill (required for auto-loading)

### Optional

- `name` - Skill name (defaults to directory name)
- `disable-model-invocation` - Set to `true` to prevent auto-loading
- `user-invocable` - Set to `false` to hide from user
- `allowed-tools` - Tools agent can use without permission

---

## How Skills Load

Skills load in two ways:

### 1. Specific Skill

```python
# Load only one skill by name
agent = deep_agent(tool, skill="paper-finder")
```

The agent loads **only** the `paper-finder` skill.

### 2. All Skills

```python
# Load all skills from assistant/skills/
agent = deep_agent(tool, all_skills=True)
```

The agent loads **all** skills and chooses which to use based on the prompt.

---

## Progressive Disclosure

DeepAgents use "progressive disclosure":

1. **At startup**: Read frontmatter from all SKILL.md files
2. **When matched**: Load full SKILL.md when user prompt matches description
3. **Execute**: Follow instructions in SKILL.md

This keeps context small until needed.

---

## Tips

### Good Descriptions

Be specific so the agent knows when to use the skill:

**Good**: `"Use when user wants to search for academic papers from PubMed or arXiv"`

**Bad**: `"Searches papers"` (too vague)

### Keep It Focused

- One skill = one workflow
- Keep SKILL.md under 500 lines
- Move detailed docs to separate files

### Reference Tools

List available tools in the instructions so the agent knows what it can use.

---

## Skill Structure

```
assistant/skills/
└── my-skill/
    ├── SKILL.md          # Main instructions (required)
    ├── template.md       # Optional template
    ├── examples.md       # Optional examples
    └── scripts/
        └── helper.sh     # Optional scripts
```

Only `SKILL.md` is required. Add other files as needed.

---

## Advanced: Multiple Files

Skills can include multiple files:

```markdown
---
name: complex-skill
description: Complex workflow with templates
---

# Complex Skill

## Instructions
1. Read [template.md](template.md) for the format
2. See [examples.md](examples.md) for examples
3. Use the template to create output
```

Reference files from SKILL.md so the agent knows when to load them.

---

## Examples

See existing skills in `assistant/skills/`:
- `paper-finder/` - Search academic papers

---

## Testing Skills

Create a test to verify your skill works:

```python
from assistant.agents.deepAgent import deep_agent
from assistant.tools.research.articles import search_papers

# Test the skill
agent = deep_agent(search_papers, skill="paper-finder")
response = agent.call("Find quantum computing papers")

print(response)
```

---

## Troubleshooting

### Skill not loading

- Check directory name matches skill name in frontmatter
- Verify SKILL.md exists in `assistant/skills/your-skill/`
- Check description is specific enough

### Agent doesn't use skill

- Make your prompt match the skill description
- Try using `skill="name"` to force loading
- Check skill instructions are clear

---

## Resources

- See `assistant/skills/README.md` for more details
- See `assistant/agents/README.md` for agent usage
- Example skills in `assistant/skills/`
