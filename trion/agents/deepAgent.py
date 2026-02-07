"""
DeepAgent utilities - Advanced agents with skills, planning, and file access

Minimal usage:
    from trion.agents.deepAgent import deep_agent
    from trion.tools.research.articles import search_papers

    agent = deep_agent(search_papers)
    response = agent.call("Find papers about CRISPR")
    print(response)

With skill:
    agent = deep_agent(search_papers, skill="paper-finder")
    response = agent.call("Find papers about CRISPR")

With custom LLM:
    agent = deep_agent(search_papers, llm_type="reasoning")
    response = agent.call("Complex research task")

With system prompt:
    agent = deep_agent(
        search_papers,
        system_prompt="You are a medical research specialist"
    )
"""

from deepagents import create_deep_agent
from langchain_ollama import ChatOllama
from typing import Optional
from pathlib import Path
from trion.utils.config import CONFIG


class DeepAgent:
    """Wrapper around DeepAgent with simple call() interface"""

    def __init__(self, agent):
        self._agent = agent

    def call(self, prompt: str) -> str:
        """
        Call the agent with a simple prompt string.

        Args:
            prompt: What you want the agent to do

        Returns:
            Response as a plain string (not nested dict)
        """
        response = self._agent.invoke({
            "messages": [{"role": "user", "content": prompt}]
        })
        return response["messages"][-1].content

    def invoke(self, *args, **kwargs):
        """Raw invoke method for advanced usage"""
        return self._agent.invoke(*args, **kwargs)


def deep_agent(
    *tools,
    skill: Optional[str] = None,
    llm_type: str = "function_calling",
    system_prompt: str = "You are a helpful AI assistant.",
    all_skills: bool = False
):
    """
    Create a DeepAgent with simple call() interface.

    DeepAgents are advanced agents with:
    - Skills: Reusable capability bundles
    - Planning: Built-in task decomposition
    - File access: ls, read_file, write_file, edit_file
    - Subagents: Spawn specialized agents

    Usage:
        # Basic
        agent = deep_agent(tool1, tool2)
        response = agent.call("Do something")

        # With specific skill
        agent = deep_agent(tool1, skill="paper-finder")
        response = agent.call("Find papers")

        # With all skills
        agent = deep_agent(tool1, all_skills=True)

        # Custom LLM
        agent = deep_agent(tool1, llm_type="reasoning")

        # Custom prompt
        agent = deep_agent(tool1, system_prompt="You are a specialist")

    Args:
        *tools: Tools to give the agent
        skill: Load specific skill by name (e.g., "paper-finder")
        llm_type: Which LLM config (function_calling, reasoning, general)
        system_prompt: System instructions
        all_skills: Load all skills from trion/skills/ (default: False)

    Returns:
        DeepAgent with simple .call(prompt) method
    """
    # Get LLM config
    llm_config = CONFIG.get("llm", {}).get(
        llm_type,
        CONFIG.get("llm", {}).get("function_calling", {})
    )

    # Create LLM
    llm = ChatOllama(
        model=llm_config.get("model", "qwen2.5:latest"),
        base_url=llm_config.get("base_url", "http://localhost:11434"),
        temperature=llm_config.get("temperature", 0.7)
    )

    # Determine skills to load
    skills_path = None
    builtin_skills_dir = Path(__file__).parent.parent / "skills"
    user_skills_dir = Path.home() / ".trion" / "skills"

    if skill:
        # Load specific skill by name - check built-in first, then user skills
        skill_path = builtin_skills_dir / skill
        if skill_path.exists():
            skills_path = [str(skill_path.parent)]
        else:
            # Try user skills directory
            skill_path = user_skills_dir / skill
            if skill_path.exists():
                skills_path = [str(skill_path.parent)]
            else:
                print(f"Warning: Skill '{skill}' not found in built-in or user skills")

    elif all_skills:
        # Load all skills from both built-in and user directories
        skills_path = []
        if builtin_skills_dir.exists():
            skills_path.append(str(builtin_skills_dir))
        if user_skills_dir.exists():
            skills_path.append(str(user_skills_dir))
        if not skills_path:
            skills_path = None

    # Create agent
    agent = create_deep_agent(
        model=llm,
        tools=list(tools) if tools else None,
        skills=skills_path,
        system_prompt=system_prompt
    )

    return DeepAgent(agent)
