"""Dependencias semánticas de cada sección MGA + normalización tab -> sección."""

from __future__ import annotations

from typing import Dict, List, Optional, Set


class UnknownSectionError(ValueError):
    """Se lanza cuando un `tab`/`section` no puede normalizarse a una clave canónica."""


# Vocabulario interno único que debe usar la capa de IA (loaders, ContextManager).
CANONICAL_SECTIONS: Set[str] = {
    "development_plans",
    "problems",
    "participants",
    "population",
    "objectives",
    "alternatives",
    "requirements",
    "technical_analysis",
    "localization",
    "value_chain",
}

# Aliases reales observados en frontend (tabs), nombres de tabla y subtablas.
# Ver frontend/src/types/project.ts (MGASection) y
# backend/app/models/chat_history.py (_get_valid_tabs / normalización singular-plural).
_SECTION_ALIASES: Dict[str, str] = {
    # development_plans
    "development_plans": "development_plans",
    "development_plan": "development_plans",
    "pnds": "development_plans",
    "pnd": "development_plans",
    # pnd_details es una tabla global (sin project_id); se normaliza a la misma
    # sección para fines de tab, pero el loader NO debe usarla (ver context_loaders.py).
    "pnd_details": "development_plans",
    # problems (árbol de problemas)
    "problems": "problems",
    "problem": "problems",
    "direct_effects": "problems",
    "indirect_effects": "problems",
    "direct_causes": "problems",
    "indirect_causes": "problems",
    # participants
    "participants_general": "participants",
    "participants": "participants",
    # population
    "population": "population",
    "affected_population": "population",
    "intervention_population": "population",
    "characteristics_population": "population",
    # objectives
    "objectives": "objectives",
    "objectives_causes": "objectives",
    "objectives_indicator": "objectives",
    "objectives_indicators": "objectives",
    # alternatives
    "alternatives_general": "alternatives",
    "alternatives": "alternatives",
    # requirements
    "requirements_general": "requirements",
    "requirements": "requirements",
    # localization
    "localization_general": "localization",
    "localization": "localization",
    # technical_analysis
    "technical_analysis": "technical_analysis",
    # value_chain (tabla real es plural "value_chains"; el tab del frontend usa singular)
    "value_chain": "value_chain",
    "value_chains": "value_chain",
    "value_chain_objectives": "value_chain",
    "products": "value_chain",
    "activities": "value_chain",
}


def normalize_section(tab: Optional[str]) -> str:
    """Normaliza un `tab`/nombre de tabla a su clave canónica de sección MGA.

    - Case-insensitive y tolerante a guiones ("-" -> "_").
    - Rechaza explícitamente valores desconocidos (UnknownSectionError) en vez
      de adivinar; el llamador decide si usar un fallback (p. ej. "default").
    """
    if not tab or not str(tab).strip():
        raise UnknownSectionError("Section/tab vacío o nulo")

    key = str(tab).strip().lower().replace("-", "_")
    canonical = _SECTION_ALIASES.get(key)
    if canonical is None:
        raise UnknownSectionError(f"Tab/sección desconocida: '{tab}'")
    return canonical


# Objeto semántico "actual" (principal) de cada sección canónica. Ver punto 22.
SECTION_CURRENT: Dict[str, Optional[str]] = {
    "development_plans": "planning_alignment",
    "problems": "problem_tree",
    "participants": "participants",
    "population": "population",
    "objectives": "objectives",
    # El objeto "current" de la sección alternatives es TODAS las alternativas
    # registradas (no solo la activa). `selected_alternative` es un objeto
    # semántico independiente, usado por requirements/technical_analysis/
    # localization/value_chain (ver context_loaders.py).
    "alternatives": "alternatives",
    "requirements": "requirements",
    "technical_analysis": "technical_analysis",
    "localization": "localization",
    "value_chain": "value_chain",
    "default": None,
}


# NOTA: por compatibilidad con el renderer legado (`ContextManager._render_semantic_block`
# vía `project_data`), `required` incluye el bloque "current" de la sección; los
# consumidores nuevos (build_semantic_context) excluyen el `current` de `required`.
SECTION_DEPENDENCIES: Dict[str, Dict[str, List[str]]] = {
    "development_plans": {
        "required": ["project", "planning_alignment"],
        "supporting": [],
        "forbidden_generation": [],
    },
    "problems": {
        "required": ["project", "planning_alignment", "problem_tree"],
        "supporting": [],
        "forbidden_generation": ["objectives", "alternatives", "value_chain"],
    },
    "participants": {
        "required": ["project", "problem_summary", "participants"],
        "supporting": ["participants_summary"],
        "forbidden_generation": ["alternatives", "value_chain"],
    },
    "population": {
        "required": ["project", "problem_summary", "population"],
        "supporting": ["participants_summary"],
        "forbidden_generation": ["alternatives", "value_chain"],
    },
    "objectives": {
        "required": ["project", "problem_tree", "planning_alignment", "objectives"],
        "supporting": ["problem_summary"],
        "forbidden_generation": ["value_chain"],
    },
    "alternatives": {
        "required": ["project", "objectives", "alternatives"],
        "supporting": ["problem_summary", "population_summary", "participants_summary"],
        "forbidden_generation": ["value_chain"],
    },
    "requirements": {
        "required": ["project", "selected_alternative", "objectives", "population", "requirements"],
        "supporting": [],
        "forbidden_generation": ["value_chain"],
    },
    "technical_analysis": {
        "required": ["project", "selected_alternative", "requirements", "technical_analysis"],
        "supporting": ["objectives_summary"],
        "forbidden_generation": ["value_chain"],
    },
    "localization": {
        "required": ["project", "selected_alternative", "requirements", "intervention_population", "localization"],
        "supporting": ["technical_analysis"],
        "forbidden_generation": ["value_chain"],
    },
    "value_chain": {
        "required": ["project", "objectives", "selected_alternative", "requirements", "value_chain"],
        "supporting": ["technical_analysis"],
        "forbidden_generation": [],
    },
    "default": {
        "required": ["project"],
        "supporting": [],
        "forbidden_generation": [],
    },
}


def _resolve_section_key(section: str) -> str:
    normalized = (section or "default").lower().replace("-", "_")
    return _SECTION_ALIASES.get(normalized, normalized)


def get_section_dependencies(section: str, mode: str = "generation") -> Dict[str, List[str]]:
    section_key = _resolve_section_key(section)
    deps = SECTION_DEPENDENCIES.get(section_key, SECTION_DEPENDENCIES["default"]).copy()

    if mode == "validation":
        validated: Dict[str, List[str]] = {"required": list(deps["required"]), "supporting": list(deps["supporting"])}
        if section_key == "problems":
            validated["supporting"] = ["objectives", "alternatives"]
        elif section_key == "objectives":
            validated["supporting"] = ["alternatives", "value_chain"]
        return validated

    return {"required": list(deps["required"]), "supporting": list(deps["supporting"])}


def get_forbidden_sections(section: str, mode: str = "generation") -> Set[str]:
    section_key = _resolve_section_key(section)
    return set(SECTION_DEPENDENCIES.get(section_key, SECTION_DEPENDENCIES["default"]).get("forbidden_generation", []))


def get_section_current(section: str) -> Optional[str]:
    """Devuelve el nombre del objeto semántico "current"/principal de la sección."""
    section_key = _resolve_section_key(section)
    return SECTION_CURRENT.get(section_key)
