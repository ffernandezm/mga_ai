"""OpenAI LLM Integration for MGA."""

from __future__ import annotations

import os

from langchain_openai import ChatOpenAI


def resolve_openai_model(model_name: str) -> str:
    """Valida y devuelve el ID real configurado por el administrador."""
    resolved = (model_name or "").strip()
    if not resolved:
        raise ValueError("OPENAI_MODEL debe contener un ID de modelo real")
    return resolved


class OpenAILLM:
    """Wrapper de ChatOpenAI para uso consistente en el backend."""

    def __init__(self, model_name: str = "", api_key: str | None = None):
        api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY no configurada en .env")

        self.model_name = resolve_openai_model(model_name)
        self.model = ChatOpenAI(
            model=self.model_name,
            api_key=api_key,
            temperature=0.7,
        )

    def get_model(self) -> ChatOpenAI:
        """Retorna la instancia inicializada de ChatOpenAI."""
        return self.model