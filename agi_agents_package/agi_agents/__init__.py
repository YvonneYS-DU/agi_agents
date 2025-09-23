"""
AGI Agent - A streamlined interface for LangChain AI agent creation.

This package provides a simplified API for creating and managing AI agents
with multi-modal support (text and images) using LangChain framework.

Author: YvonneYS-Du
Version: 0.2.1
Date: Aug 2025
"""

from .agi_agent import Agents, Contexts, Document

__version__ = "0.2.1"
__all__ = ["Agents", "Contexts", "Document"]