"""Utilidad de diagnóstico: mide el tamaño real (tokens) de un prompt.

Solo para uso en desarrollo/tests. NO trunca nada, únicamente mide. Ver
`TOKEN_METHOD` para el método de conteo realmente usado en este entorno.
"""

from __future__ import annotations

from dataclasses import dataclass, asdict

try:
    import tiktoken

    _ENCODING = tiktoken.get_encoding("cl100k_base")
    # cl100k_base es el tokenizer de OpenAI (gpt-3.5/4). Groq (Llama) y Gemini
    # no exponen un tokenizer propio de forma sencilla en Python, por lo que
    # se usa como aproximación razonable multi-modelo (no es un conteo exacto
    # para Groq/Gemini).
    TOKEN_METHOD = "tiktoken:cl100k_base (aproximación; Groq/Gemini no exponen tokenizer propio)"
except Exception:  # pragma: no cover - fallback si tiktoken no está disponible
    _ENCODING = None
    TOKEN_METHOD = "heuristica: len(texto) // 4 caracteres por token (tiktoken no disponible)"


def count_tokens(text: str) -> int:
    """Cuenta tokens de un texto según `TOKEN_METHOD`."""
    if not text:
        return 0
    if _ENCODING is not None:
        return len(_ENCODING.encode(text))
    return max(1, len(text) // 4)


@dataclass
class PromptTokenReport:
    """Desglose de tokens estimados por bloque del prompt final."""

    section: str
    system_tokens: int
    project_context_tokens: int
    rag_context_tokens: int
    history_tokens: int
    question_tokens: int
    estimated_total_tokens: int
    token_method: str = TOKEN_METHOD

    def as_dict(self) -> dict:
        return asdict(self)
