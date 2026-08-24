"""
OpenAI LLM Integration for MGA.

Modelos integrados:
- gpt-5.6-luna: Desarrollo y pruebas frecuentes
- gpt-5.6-terra: Verificación previa y ajuste
- gpt-5.6-sol: Evaluación final
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Dict, List

from langchain_openai import ChatOpenAI


DEFAULT_OPENAI_MODEL = "gpt-5.6-luna"


@dataclass(frozen=True)
class OpenAIModelProfile:
    """Describe un modelo OpenAI disponible y su uso recomendado."""

    model_name: str
    usage: str


OPENAI_MODEL_PROFILES: Dict[str, OpenAIModelProfile] = {
    "gpt-5.6-luna": OpenAIModelProfile(
        model_name="gpt-5.6-luna",
        usage="Desarrollo y pruebas frecuentes",
    ),
    "gpt-5.6-terra": OpenAIModelProfile(
        model_name="gpt-5.6-terra",
        usage="Verificación previa y ajuste",
    ),
    "gpt-5.6-sol": OpenAIModelProfile(
        model_name="gpt-5.6-sol",
        usage="Modelo seleccionado para evaluación final",
    ),
}


def resolve_openai_model(model_name: str) -> str:
    """Resuelve el nombre de modelo OpenAI y valida que esté soportado."""
    normalized = (model_name or "").strip().lower()
    profile = OPENAI_MODEL_PROFILES.get(normalized)

    if profile is None:
        valid_models = ", ".join(sorted(OPENAI_MODEL_PROFILES))
        raise ValueError(
            f"Modelo OpenAI no soportado: '{model_name}'. "
            f"Modelos válidos: {valid_models}"
        )

    return profile.model_name


def get_openai_model_profiles() -> List[OpenAIModelProfile]:
    """Retorna los perfiles de modelos OpenAI soportados."""
    return [OPENAI_MODEL_PROFILES[key] for key in sorted(OPENAI_MODEL_PROFILES.keys())]


class OpenAILLM:
    """Wrapper de ChatOpenAI para uso consistente en el backend."""

    def __init__(self, model_name: str = DEFAULT_OPENAI_MODEL, api_key: str | None = None):
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