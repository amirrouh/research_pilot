"""Trion - Transdisciplinary Research Intelligence & Opportunity Navigation"""

__version__ = "0.1.0"

# Core functionality
from trion.agents.core import agent
from trion.agents.deepAgent import deep_agent

# Management functions
from trion.management import (
    create_skill,
    create_tool,
    list_skills,
    list_tools,
    get_skill_info,
)

__all__ = [
    "agent",
    "deep_agent",
    "create_skill",
    "create_tool",
    "list_skills",
    "list_tools",
    "get_skill_info",
    "__version__",
]
