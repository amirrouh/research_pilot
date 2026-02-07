"""Configuration loading utilities

This module provides configuration loading that searches for config.yaml
in the following order:
1. Current directory and upward (until reaching root)
2. ~/.trion/config.yaml
3. Default configuration (Ollama defaults)
"""

from pathlib import Path
from typing import Optional
import yaml


def find_config(start_path: Optional[Path] = None) -> Optional[Path]:
    """
    Find config.yaml by searching upward from start_path.

    Search order:
    1. Current directory and upward
    2. ~/.trion/config.yaml
    3. None (will use defaults)

    Args:
        start_path: Starting directory (default: current working directory)

    Returns:
        Path to config.yaml if found, None otherwise
    """
    current = start_path or Path.cwd()

    # Search upward until we find config.yaml or hit root
    while current != current.parent:
        config_path = current / "config.yaml"
        if config_path.exists():
            return config_path
        current = current.parent

    # Fallback to user home config
    home_config = Path.home() / ".trion" / "config.yaml"
    if home_config.exists():
        return home_config

    return None


def load_config() -> dict:
    """
    Load configuration from config.yaml.

    Returns default Ollama configuration if no config file is found.

    Returns:
        Configuration dictionary with LLM settings
    """
    config_path = find_config()

    if config_path is None:
        # Return default Ollama config
        return {
            "llm": {
                "general": {
                    "model": "qwen2.5:latest",
                    "base_url": "http://localhost:11434",
                    "temperature": 0.7,
                }
            }
        }

    with open(config_path) as f:
        return yaml.safe_load(f)


# Global config instance
# This is loaded once when the module is imported
CONFIG = load_config()
