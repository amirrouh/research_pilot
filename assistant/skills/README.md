# Skills Directory

Skills are reusable capability bundles that DeepAgents can load automatically.

## Structure

```
assistant/skills/
└── skill-name/
    └── SKILL.md
```

## Creating a Skill

1. **Create directory**: `mkdir assistant/skills/my-skill`
2. **Create SKILL.md** with frontmatter and instructions:

```markdown
---
name: my-skill
description: When to use this skill (be specific)
---

# Skill Name

## Overview
What this skill does

## Instructions
Step-by-step guidance for the agent

## Available Tools
- tool_name: What it does
```

3. **That's it!** The skill auto-loads when you create a DeepAgent.

## Using Skills

Skills load automatically:

```python
from assistant.agents.deepAgent import deep_agent
from assistant.tools.some_tool import my_tool

# Skills auto-load from assistant/skills/
agent = deep_agent(my_tool)

# Agent uses skills when user request matches description
response = agent.invoke({
    "messages": [{"role": "user", "content": "Do something"}]
})
```

## Frontmatter Fields

Only `description` is required. Optional fields:

- `name`: Skill name (defaults to directory name)
- `description`: When to use this skill (REQUIRED for auto-loading)
- `disable-model-invocation`: Set to `true` to prevent auto-loading
- `user-invocable`: Set to `false` to hide from user
- `allowed-tools`: Tools agent can use without permission when skill active

## Tips

- Keep descriptions specific so agent knows when to use the skill
- Reference available tools in the instructions
- Keep SKILL.md under 500 lines (use separate files for long docs)
- Test your skill to verify it loads correctly
