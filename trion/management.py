"""Management functions for Trion"""

import inspect
from pathlib import Path
from typing import Union, Optional, Callable
from langchain.tools import tool
import yaml


def create_skill(
    name: Optional[str] = None,
    description: Optional[str] = None,
    instructions: Optional[str] = None,
    markdown_path: Optional[Union[str, Path]] = None,
    output_dir: Optional[Union[str, Path]] = None
) -> Path:
    """
    Create a new skill programmatically.

    Usage:
        # From markdown file
        create_skill(markdown_path="path/to/skill.md")

        # From parameters
        create_skill(
            name="my-skill",
            description="What it does",
            instructions="1. Step one\\n2. Step two"
        )

    Args:
        name: Skill name (required if not using markdown_path)
        description: Skill description
        instructions: Skill instructions
        markdown_path: Path to SKILL.md file (alternative to parameters)
        output_dir: Where to save skill (default: ~/.trion/skills/)

    Returns:
        Path to created skill directory
    """
    # If markdown_path provided, read from file
    if markdown_path:
        return _create_skill_from_file(markdown_path, output_dir)

    # Otherwise create from parameters
    if not name:
        raise ValueError("Either markdown_path or name must be provided")

    # Default output directory
    if output_dir is None:
        output_dir = Path.home() / ".trion" / "skills"
    else:
        output_dir = Path(output_dir)

    # Create skill directory
    skill_dir = output_dir / name
    skill_dir.mkdir(parents=True, exist_ok=True)

    # Create SKILL.md
    skill_md = skill_dir / "SKILL.md"
    content = f"""---
name: {name}
description: {description or 'Custom skill'}
---

# {name.replace('-', ' ').title()}

## Overview
{description or 'Custom skill'}

## Instructions
{instructions or '1. Step one\\n2. Step two\\n3. Step three'}
"""
    skill_md.write_text(content)

    return skill_dir


def _create_skill_from_file(
    markdown_path: Union[str, Path],
    output_dir: Optional[Union[str, Path]] = None
) -> Path:
    """Create skill from markdown file"""
    markdown_path = Path(markdown_path)

    if not markdown_path.exists():
        raise FileNotFoundError(f"Skill file not found: {markdown_path}")

    # Read file and parse frontmatter
    content = markdown_path.read_text()

    # Extract name from frontmatter
    if content.startswith("---"):
        parts = content.split("---", 2)
        if len(parts) >= 3:
            frontmatter = yaml.safe_load(parts[1])
            name = frontmatter.get("name")
            if not name:
                raise ValueError("Skill file must have 'name' in frontmatter")
        else:
            raise ValueError("Invalid skill file format")
    else:
        # Use filename as name
        name = markdown_path.stem

    # Default output directory
    if output_dir is None:
        output_dir = Path.home() / ".trion" / "skills"
    else:
        output_dir = Path(output_dir)

    # Create skill directory and copy file
    skill_dir = output_dir / name
    skill_dir.mkdir(parents=True, exist_ok=True)

    skill_file = skill_dir / "SKILL.md"
    skill_file.write_text(content)

    return skill_dir


def create_tool(
    name: str,
    function: Callable,
    description: str,
    output_path: Optional[Union[str, Path]] = None
):
    """
    Create a LangChain tool from a function.

    Usage:
        def my_function(query: str) -> str:
            # Implementation
            return result

        tool = create_tool(
            name="my_tool",
            function=my_function,
            description="Custom tool"
        )

    Args:
        name: Tool name
        function: Python function to wrap
        description: Description for LLM
        output_path: Where to save tool file (optional)

    Returns:
        LangChain tool object
    """
    # Create wrapper function with custom name and description
    def wrapper(*args, **kwargs):
        return function(*args, **kwargs)

    # Set function name and docstring
    wrapper.__name__ = name
    wrapper.__doc__ = description

    # Create tool from wrapper
    tool_func = tool(wrapper)

    # Optionally save to file
    if output_path:
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        # Generate tool file
        code = f'''"""Auto-generated tool: {name}"""

from langchain.tools import tool

{inspect.getsource(function)}

@tool
def {name}(*args, **kwargs):
    """{description}"""
    return {function.__name__}(*args, **kwargs)
'''
        output_path.write_text(code)

    return tool_func


def list_skills() -> dict:
    """
    List all available skills.

    Returns:
        Dictionary with 'built_in', 'user', and 'all' skill lists
    """
    # Check built-in skills
    builtin_skills_dir = Path(__file__).parent / "skills"
    builtin_skills = []
    if builtin_skills_dir.exists():
        builtin_skills = [
            d.name for d in builtin_skills_dir.iterdir()
            if d.is_dir() and (d / "SKILL.md").exists()
        ]

    # Check user skills
    user_skills_dir = Path.home() / ".trion" / "skills"
    user_skills = []
    if user_skills_dir.exists():
        user_skills = [
            d.name for d in user_skills_dir.iterdir()
            if d.is_dir() and (d / "SKILL.md").exists()
        ]

    return {
        "built_in": builtin_skills,
        "user": user_skills,
        "all": builtin_skills + user_skills
    }


def list_tools() -> dict:
    """
    List all available tools by category.

    Returns:
        Dictionary mapping category names to lists of tool names
    """
    # Scan tools directory
    tools_dir = Path(__file__).parent / "tools"
    tools = {}

    if not tools_dir.exists():
        return tools

    for category_dir in tools_dir.iterdir():
        if category_dir.is_dir() and category_dir.name != "__pycache__":
            category = category_dir.name
            tools[category] = []

            for tool_file in category_dir.glob("*.py"):
                if tool_file.name != "__init__.py":
                    tools[category].append(tool_file.stem)

    return tools


def get_skill_info(name: str) -> dict:
    """
    Get skill metadata and content.

    Args:
        name: Skill name

    Returns:
        Dictionary with skill information (name, description, path, content)

    Raises:
        ValueError: If skill not found
    """
    # Check built-in first
    builtin_path = Path(__file__).parent / "skills" / name / "SKILL.md"
    if builtin_path.exists():
        skill_path = builtin_path
    else:
        # Check user skills
        user_path = Path.home() / ".trion" / "skills" / name / "SKILL.md"
        if user_path.exists():
            skill_path = user_path
        else:
            raise ValueError(f"Skill not found: {name}")

    # Parse SKILL.md
    content = skill_path.read_text()

    if content.startswith("---"):
        parts = content.split("---", 2)
        if len(parts) >= 3:
            frontmatter = yaml.safe_load(parts[1])
            body = parts[2].strip()
            return {
                "name": frontmatter.get("name", name),
                "description": frontmatter.get("description", ""),
                "path": str(skill_path.parent),
                "content": body
            }

    return {
        "name": name,
        "path": str(skill_path.parent),
        "content": content
    }
