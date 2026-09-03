"""Canonical selectable-field metadata shared by semantic context and validation."""

from __future__ import annotations

from pathlib import Path
from typing import Dict, List, Optional


_FRONTEND_DATA = Path(__file__).resolve().parents[4] / "frontend" / "src" / "data"


def _pairs(values: List[str]) -> List[Dict[str, str]]:
    return [{"value": value, "label": value} for value in sorted(set(values)) if value]


def _participant_domains() -> Dict[str, List[Dict[str, str]]]:
    rows = []
    source = _FRONTEND_DATA / "participantes.csv"
    if source.exists():
        for line in source.read_text(encoding="utf-8").splitlines()[1:]:
            actor, _, entity = line.partition(";")
            actor, entity = actor.strip().strip('"'), entity.strip().strip('"')
            if actor:
                rows.append((actor, entity))
    actors = _pairs([actor for actor, _ in rows])
    entities = _pairs([entity for _, entity in rows if entity and entity not in {"Seleccione", "Departamento"}])
    return {"participant_actor": actors, "participant_entity": entities}


def get_select_metadata(field_key: str) -> Optional[Dict]:
    domains = _participant_domains()
    catalog = {
        "participant_actor": {"label_es": "Actor", "allowed_values": domains["participant_actor"]},
        "participant_entity": {"label_es": "Entidad", "allowed_values": domains["participant_entity"]},
        "rol": {"label_es": "Rol", "allowed_values": _pairs(["Beneficiario", "Cooperante", "Oponente", "Perjudicado"])},
        "territorial_level": {"label_es": "Nivel territorial del plan", "allowed_values": _pairs(["departmental", "municipal"])},
        "administrative_level": {"label_es": "Nivel territorial", "allowed_values": _pairs(["departmental", "municipal"])},
    }
    metadata = catalog.get(field_key)
    return {"field_key": field_key, **metadata} if metadata else None


def validate_suggested_value(field_key: str, value: str) -> bool:
    """Only accepts exact values that belong to the current selectable domain."""
    metadata = get_select_metadata(field_key)
    if not metadata:
        return False
    return value in {item["value"] for item in metadata["allowed_values"]}


def get_suggestable_field(field_key: str) -> Optional[Dict[str, str]]:
    """Fields that can be safely staged in a simple local form control."""
    fields = {
        "central_problem": {"label_es": "Problema central", "field_type": "text"},
        "current_description": {"label_es": "Descripción de la situación existente", "field_type": "textarea"},
        "magnitude_problem": {"label_es": "Magnitud del problema", "field_type": "textarea"},
        "general_objective": {"label_es": "Objetivo general", "field_type": "textarea"},
        "analysis": {"label_es": "Análisis técnico", "field_type": "textarea"},
    }
    metadata = fields.get(field_key)
    return {"field_key": field_key, **metadata} if metadata else None