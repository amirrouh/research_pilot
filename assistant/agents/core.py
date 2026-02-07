"""
Core agent utilities

Usage:
    from assistant.agents.core import agent
    from assistant.tools.research.articles import search_papers

    my_agent = agent(search_papers)
    response = my_agent.call("Find papers about CRISPR")
"""

from langchain_ollama import ChatOllama
from langchain_core.messages import HumanMessage, SystemMessage
from typing import Optional
import yaml
from pathlib import Path


def _load_config():
    """Load configuration from config.yaml"""
    config_path = Path(__file__).parent.parent.parent / "config.yaml"

    if config_path.exists():
        with open(config_path) as f:
            return yaml.safe_load(f)
    else:
        # Default fallback
        return {
            "llm": {
                "model": "qwen2.5:latest",
                "base_url": "http://192.168.1.92:11434",
                "temperature": 0.7
            }
        }


# Load LLM config
LLM_CONFIG = _load_config().get("llm", {})


class _Agent:
    """Agent instance with tools"""

    def __init__(self, llm_with_tools, tools, system_message: str):
        self.llm = llm_with_tools
        self.tools = {tool.name: tool for tool in tools} if tools else {}
        self.system_message = system_message

    def call(self, prompt: str) -> str:
        """Call the agent with a prompt"""
        messages = [
            SystemMessage(content=self.system_message),
            HumanMessage(content=prompt)
        ]

        # Get initial response
        response = self.llm.invoke(messages)

        # If model wants to use tools, execute them
        if hasattr(response, 'tool_calls') and response.tool_calls:
            from langchain_core.messages import ToolMessage

            # Add AI response to messages
            messages.append(response)

            # Execute each tool
            for tool_call in response.tool_calls:
                tool = self.tools.get(tool_call['name'])
                if tool:
                    result = tool.invoke(tool_call['args'])
                    messages.append(
                        ToolMessage(
                            content=str(result),
                            tool_call_id=tool_call['id']
                        )
                    )

            # Get final response after tool execution
            response = self.llm.invoke(messages)

        return response.content


def agent(*tools, llm_type: str = "general", system_message: str = "You are a helpful AI assistant."):
    """
    Create an agent with tools.

    Usage:
        my_agent = agent(tool1, tool2)
        my_agent = agent(tool1, llm_type="reasoning")
        response = my_agent.call("Do something")

    Args:
        *tools: Tools to give the agent (pass them directly)
        llm_type: Which LLM to use (general, function_calling, reasoning, vision). Default: general
        system_message: System instructions (optional)

    Returns:
        Agent instance ready to call
    """
    # Get LLM config for specified type
    llm_config = LLM_CONFIG.get(llm_type, LLM_CONFIG.get("general", {}))

    # Create LLM from config
    llm = ChatOllama(
        model=llm_config.get("model", "qwen2.5:latest"),
        base_url=llm_config.get("base_url", "http://localhost:11434"),
        temperature=llm_config.get("temperature", 0.7)
    )

    # Bind tools if provided
    if tools:
        llm = llm.bind_tools(list(tools))

    return _Agent(llm, list(tools), system_message)
