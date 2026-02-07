# Management Functions

Trion provides programmatic functions to create and manage skills and tools.

## Overview

```python
from trion import (
    create_skill,      # Create custom skills
    create_tool,       # Create custom tools
    list_skills,       # List available skills
    list_tools,        # List available tools
    get_skill_info,    # Get skill details
)
```

## Creating Skills

### From Parameters

```python
from trion import create_skill

skill_path = create_skill(
    name="literature-review",
    description="Review academic literature systematically",
    instructions="""
1. Search for papers on the specified topic
2. Extract key findings from each paper
3. Identify common themes and trends
4. Summarize the state of research
"""
)

print(f"Created at: {skill_path}")
# Output: Created at: /Users/you/.trion/skills/literature-review
```

### From Markdown File

```python
# Create SKILL.md
"""
---
name: grant-finder
description: Find relevant grant opportunities
---

# Grant Finder

## Instructions
1. Understand the research area
2. Search NIH grants database
3. Filter by relevance and deadline
4. Summarize top opportunities
"""

# Create skill from file
from trion import create_skill

skill_path = create_skill(markdown_path="grant-finder.md")
```

### Using Created Skills

```python
from trion import deep_agent
from trion.tools.research.articles import search_papers

# Use your custom skill
agent = deep_agent(search_papers, skill="literature-review")
response = agent.call("Review machine learning papers from 2024")
```

## Creating Tools

### Basic Tool Creation

```python
from trion import create_tool

def calculate_impact_factor(citations: int, years: int) -> float:
    """Calculate approximate impact factor"""
    return citations / years if years > 0 else 0.0

# Convert to LangChain tool
tool = create_tool(
    name="calculate_impact_factor",
    function=calculate_impact_factor,
    description="Calculate impact factor from citations and years"
)

# Use with agent
from trion import agent

my_agent = agent(tool)
response = my_agent.call("Calculate impact factor for 120 citations over 3 years")
```

### Save Tool to File

```python
from trion import create_tool

def my_function(query: str) -> str:
    return f"Processed: {query}"

# Create and save
tool = create_tool(
    name="my_tool",
    function=my_function,
    description="Custom processing tool",
    output_path="custom_tools/my_tool.py"  # Optional: save to file
)
```

## Listing Skills

```python
from trion import list_skills

skills = list_skills()

print(f"Built-in skills: {skills['built_in']}")
# Output: Built-in skills: ['paper-finder']

print(f"User skills: {skills['user']}")
# Output: User skills: ['literature-review', 'grant-finder']

print(f"All skills: {skills['all']}")
# Output: All skills: ['paper-finder', 'literature-review', 'grant-finder']
```

## Listing Tools

```python
from trion import list_tools

tools = list_tools()

for category, tool_list in tools.items():
    print(f"\n{category}:")
    for tool in tool_list:
        print(f"  - {tool}")
```

Output:
```
research:
  - articles
  - grants
  - google_scholar

document:
  - read
  - write
  - ocr

web:
  - browser
  - download
  - web_search

storage:
  - articles
  - grants

career:
  - search
```

## Getting Skill Information

```python
from trion import get_skill_info

info = get_skill_info("literature-review")

print(f"Name: {info['name']}")
print(f"Description: {info['description']}")
print(f"Path: {info['path']}")
print(f"Content:\n{info['content']}")
```

Output:
```
Name: literature-review
Description: Review academic literature systematically
Path: /Users/you/.trion/skills/literature-review
Content:
# Literature Review

## Instructions
1. Search for papers on the specified topic
...
```

## Advanced Examples

### Dynamic Skill Creation

```python
from trion import create_skill, deep_agent
from trion.tools.research.articles import search_papers

# Create different skills for different research areas
research_areas = {
    "medical": "Focus on clinical trials and medical outcomes",
    "cs": "Focus on algorithms and implementations",
    "bio": "Focus on experimental methods and biological systems"
}

for area, instructions in research_areas.items():
    create_skill(
        name=f"{area}-reviewer",
        description=f"Review {area} literature",
        instructions=instructions
    )

# Use area-specific skill
agent = deep_agent(search_papers, skill="medical-reviewer")
```

### Tool Factory Pattern

```python
from trion import create_tool

def make_formatter(style: str):
    """Factory for creating citation formatters"""

    def format_citation(title: str, authors: str, year: str) -> str:
        if style == "APA":
            return f"{authors} ({year}). {title}."
        elif style == "MLA":
            return f"{authors}. \"{title}.\" {year}."
        elif style == "Chicago":
            return f"{authors}. {year}. {title}."
        return f"{title} by {authors}, {year}"

    return format_citation

# Create multiple formatters
apa_tool = create_tool(
    name="format_apa",
    function=make_formatter("APA"),
    description="Format citations in APA style"
)

mla_tool = create_tool(
    name="format_mla",
    function=make_formatter("MLA"),
    description="Format citations in MLA style"
)
```

### Skill Templates

```python
from trion import create_skill

SKILL_TEMPLATE = """
---
name: {name}
description: {description}
---

# {title}

## Overview
{description}

## Instructions
{instructions}

## Notes
- Be thorough and systematic
- Cite sources when applicable
- Provide clear summaries
"""

def create_research_skill(name: str, focus_area: str):
    """Create a research skill with template"""

    skill_md = SKILL_TEMPLATE.format(
        name=name,
        description=f"Research assistant for {focus_area}",
        title=name.replace('-', ' ').title(),
        instructions=f"""
1. Understand the research question in {focus_area}
2. Search relevant databases
3. Analyze findings
4. Synthesize results
"""
    )

    # Save to temp file
    with open(f"/tmp/{name}.md", "w") as f:
        f.write(skill_md)

    # Create skill from file
    return create_skill(markdown_path=f"/tmp/{name}.md")

# Use factory
create_research_skill("neuroscience-researcher", "neuroscience")
create_research_skill("climate-researcher", "climate science")
```

## Best Practices

### Skill Creation

1. **Clear instructions** - Be specific about what the skill should do
2. **Appropriate scope** - One skill = one capability
3. **Descriptive names** - Use kebab-case (e.g., "literature-review")
4. **Include context** - Add notes about when to use the skill

### Tool Creation

1. **Type hints** - Always include type annotations
2. **Docstrings** - Document what the function does
3. **Clear names** - Function name becomes tool name
4. **Simple interface** - Avoid complex parameters

### Organization

1. **User skills location** - All in `~/.trion/skills/`
2. **Skill naming** - Use descriptive, unique names
3. **Version control** - Keep skill markdown in git
4. **Sharing** - Share SKILL.md files with team

## Troubleshooting

### Skill not found

```python
from trion import list_skills

skills = list_skills()
if 'my-skill' not in skills['all']:
    print("Skill not created yet or wrong name")
    print(f"Available: {skills['all']}")
```

### Tool not working

```python
# Test tool directly
from trion import create_tool

def test_func(x: str) -> str:
    return f"Result: {x}"

tool = create_tool("test", test_func, "Test tool")

# Try invoking directly
result = tool.invoke({"x": "hello"})
print(result)
```

### Clear user skills

```bash
# Remove all user skills
rm -rf ~/.trion/skills/*

# Or selectively
rm -rf ~/.trion/skills/my-skill
```

## Next Steps

- [Creating Skills](skills.md) - Deep dive into skill system
- [Using Agents](agents.md) - Agent patterns and workflows
- [Common Workflows](workflows.md) - Real-world examples
