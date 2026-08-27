"""Contexto semántico MGA para construir prompts selectivos.

NOTA: `context_loaders` (y su SEMANTIC_LOADERS) NO se importa aquí para evitar
un import circular (context_loaders -> app.models -> app.models.chat_history ->
llm_manager -> ContextManager). Impórtalo directamente desde
`app.ai.context.context_loaders` cuando lo necesites.
"""

from .context_manager import ContextManager, render_semantic_context
from .module_dependencies import (
    UnknownSectionError,
    get_section_current,
    get_section_dependencies,
    normalize_section,
)

__all__ = [
    "ContextManager",
    "render_semantic_context",
    "get_section_dependencies",
    "get_section_current",
    "normalize_section",
    "UnknownSectionError",
]
