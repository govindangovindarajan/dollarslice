"""
DollarSlice - A framework for solving problems with LLMs and function calls
"""

from .core import solve, final_answer
from .llm import create_simple_llm, create_from_ollama, LLMCall
from .utils import (
    describe_function,
    func_to_tool_json,
    func_to_one_liner,
    func_map,
    format_for_openai_tool
)

__all__ = [
    'solve',
    'final_answer',
    'create_simple_llm',
    'create_from_ollama',
    'LLMCall',
    'describe_function',
    'func_to_tool_json',
    'func_to_one_liner',
    'func_map',
    'format_for_openai_tool'
]