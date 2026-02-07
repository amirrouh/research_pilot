# Skills

Skills are reusable capability bundles for DeepAgents that auto-load from `~/.trion/skills/`.

---

## What are Skills?

Skills define specialized workflows that DeepAgents can load automatically. Each skill is a directory with a `SKILL.md` file containing:

- **Frontmatter**: Metadata (name, description)
- **Instructions**: Step-by-step guidance for the agent

**Auto-Discovery**: Just drop a skill folder in `~/.trion/skills/` and it's automatically available!

---

## Quick Start

### 1. Create Skill (Easiest Way)

```python
from trion import create_skill

create_skill(
    name="my-skill",
    description="When to use this skill",
    instructions="""
1. Step one
2. Step two
3. Step three
"""
)
```

Done! Skill is now in `~/.trion/skills/my-skill/` and automatically available.

### 2. Or Create Manually

```bash
mkdir -p ~/.trion/skills/my-skill
```

Create `~/.trion/skills/my-skill/SKILL.md`:

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

Done! Trion auto-discovers it.

### 3. Use It

```python
from trion import deep_agent
from trion.tools.research.articles import search_papers

# Skill is automatically available
agent = deep_agent(search_papers, skill="my-skill")
response = agent.call("Do something")
```

---

## Auto-Discovery

Trion automatically finds skills in two locations:

1. **Built-in**: `trion/skills/` (packaged with Trion)
2. **User**: `~/.trion/skills/` (your custom skills)

Just add/remove skill folders and Trion updates automatically!

```python
from trion import list_skills

skills = list_skills()
# {'built_in': ['paper-finder'], 'user': ['my-skill'], 'all': [...]}
```

---

## Example: Paper Finder Skill

**Built-in Location**: `trion/skills/paper-finder/SKILL.md`

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
from trion import deep_agent
from trion.tools.research.articles import search_papers

agent = deep_agent(search_papers, skill="paper-finder")
response = agent.call("Find CRISPR papers")
print(response)
```

---

## How Skills Load

Skills auto-load from `~/.trion/skills/` and built-in `trion/skills/`.

### 1. Specific Skill

```python
# Load only one skill by name
agent = deep_agent(tool, skill="paper-finder")
```

The agent loads **only** the `paper-finder` skill.

### 2. All Skills

```python
# Load all skills from both locations
agent = deep_agent(tool, all_skills=True)
```

The agent loads **all** skills and chooses which to use based on the prompt.

---

## Skill Locations

### User Skills (Your Custom Skills)
```
~/.trion/skills/
├── my-skill/
│   └── SKILL.md
├── literature-review/
│   └── SKILL.md
└── grant-finder/
    └── SKILL.md
```

### Built-in Skills (Packaged with Trion)
```
trion/skills/
└── paper-finder/
    └── SKILL.md
```

---

## Progressive Disclosure

DeepAgents use "progressive disclosure":

1. **At startup**: Read frontmatter from all SKILL.md files
2. **When matched**: Load full SKILL.md when user prompt matches description
3. **Execute**: Follow instructions in SKILL.md

This keeps context small until needed.

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
~/.trion/skills/my-skill/
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

## Share Skills

Share your skills by sharing the SKILL.md file:

```bash
# Export skill
cp ~/.trion/skills/my-skill/SKILL.md ./my-skill.md

# Share with team
git add my-skill.md
git commit -m "Add my-skill"
```

Team members can import:

```python
from trion import create_skill

create_skill(markdown_path="my-skill.md")
```

---

## Testing Skills

```python
from trion import deep_agent
from trion.tools.research.articles import search_papers

# Test the skill
agent = deep_agent(search_papers, skill="my-skill")
response = agent.call("Test query")

print(response)
```

---

## Troubleshooting

### Skill not found

```python
from trion import list_skills

skills = list_skills()
print(skills['user'])  # Check if your skill appears
```

If not listed:
- Check `~/.trion/skills/your-skill/SKILL.md` exists
- Verify frontmatter has `description` field

### Agent doesn't use skill

- Make your prompt match the skill description
- Try using `skill="name"` to force loading
- Check skill instructions are clear

### Remove skill

```bash
rm -rf ~/.trion/skills/unwanted-skill
```

Trion automatically stops finding it!

---

## Resources

- [Management Functions](management.md) - Create skills programmatically
- [Using Agents](agents.md) - Agent usage patterns
- Built-in skills: See `trion/skills/` in package
