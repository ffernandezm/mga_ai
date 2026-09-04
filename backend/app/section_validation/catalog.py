"""Catalogo canonico de campos que existen en la interfaz MGA_IA."""

from __future__ import annotations

from typing import Any, Dict, List

from app.ai.context.module_dependencies import normalize_section
from app.ai.context.select_domains import get_select_metadata


_CATALOG: Dict[str, List[Dict[str, Any]]] = {
    "development_plans": [
        {"field_key": "national_development_plan", "label_es": "Articulación con el PND", "field_type": "textarea", "required": True},
        {"field_key": "program", "label_es": "Programa relacionado", "field_type": "text", "required": True},
        {"field_key": "pnds", "label_es": "Al menos un detalle PND", "field_type": "table", "required": True},
        {"field_key": "strategy_departmental", "label_es": "Estrategia del plan departamental o sectorial", "field_type": "textarea", "required": True},
        {"field_key": "program_departmental", "label_es": "Programa del plan departamental o sectorial", "field_type": "textarea", "required": True},
        {"field_key": "strategy_district", "label_es": "Estrategia del plan distrital o municipal", "field_type": "textarea", "required": True},
        {"field_key": "program_district", "label_es": "Programa del plan distrital o municipal", "field_type": "textarea", "required": True},
        {"field_key": "strategy_other", "label_es": "Estrategia de otro plan", "field_type": "textarea", "required": True},
        {"field_key": "program_other", "label_es": "Programa de otro plan", "field_type": "textarea", "required": True},
    ],
    "problems": [
        {"field_key": "central_problem", "label_es": "Problema central", "field_type": "textarea", "required": True},
        {"field_key": "current_description", "label_es": "Descripción de la situación existente", "field_type": "textarea", "required": True},
        {"field_key": "magnitude_problem", "label_es": "Indicador o magnitud actual del problema", "field_type": "textarea", "required": True},
        {"field_key": "direct_causes", "label_es": "Al menos una causa directa", "field_type": "table", "required": True},
        {"field_key": "direct_effects", "label_es": "Al menos un efecto directo", "field_type": "table", "required": True},
    ],
    "participants": [
        {"field_key": "participants_analisis", "label_es": "Análisis general de participantes", "field_type": "textarea", "required": True},
        {"field_key": "participants", "label_es": "Al menos un participante", "field_type": "table", "required": True},
        {"field_key": "participant_actor", "label_es": "Actor", "field_type": "select", "required": True},
        {"field_key": "participant_entity", "label_es": "Entidad", "field_type": "select", "required": True},
        {"field_key": "interest_expectative", "label_es": "Intereses y expectativas", "field_type": "textarea", "required": True},
        {"field_key": "rol", "label_es": "Posición o rol", "field_type": "select", "required": True},
        {"field_key": "contribution_conflicts", "label_es": "Contribución o estrategia de gestión", "field_type": "textarea", "required": True},
    ],
    "population": [
        {"field_key": "population_number_affected", "label_es": "Cantidad de población afectada", "field_type": "number", "required": True},
        {"field_key": "population_info_affected", "label_es": "Fuente e información de población afectada", "field_type": "textarea", "required": True},
        {"field_key": "population_number_intervention", "label_es": "Cantidad de población objetivo", "field_type": "number", "required": True},
        {"field_key": "population_info_intervention", "label_es": "Fuente y criterio de población objetivo", "field_type": "textarea", "required": True},
    ],
    "objectives": [
        {"field_key": "general_objective", "label_es": "Objetivo general", "field_type": "textarea", "required": True},
        {"field_key": "specific_objectives", "label_es": "Al menos un objetivo específico", "field_type": "table", "required": True},
        {"field_key": "objectives_indicators", "label_es": "Indicador de resultado y meta", "field_type": "table", "required": True},
        {"field_key": "indicator", "label_es": "Indicador de resultado", "field_type": "text", "required": True},
        {"field_key": "meta", "label_es": "Meta del indicador", "field_type": "number", "required": True},
    ],
    "alternatives": [{"field_key": "alternatives", "label_es": "Al menos una alternativa", "field_type": "table", "required": True}, {"field_key": "alternative_name", "label_es": "Nombre o descripción de la alternativa", "field_type": "text", "required": True}],
    "requirements": [
        {"field_key": "requirements_analysis", "label_es": "Análisis de necesidades", "field_type": "textarea", "required": True},
        {"field_key": "requirements", "label_es": "Al menos un bien o servicio", "field_type": "table", "required": True},
        {"field_key": "good_service_name", "label_es": "Bien o servicio", "field_type": "text", "required": True},
        {"field_key": "unit_of_measure", "label_es": "Unidad de medida", "field_type": "text", "required": True},
        {"field_key": "supply_description", "label_es": "Información de oferta", "field_type": "textarea", "required": True},
        {"field_key": "demand_description", "label_es": "Información de demanda", "field_type": "textarea", "required": True},
        {"field_key": "start_year", "label_es": "Año de inicio", "field_type": "number", "required": True},
        {"field_key": "end_year", "label_es": "Año de fin", "field_type": "number", "required": True},
        {"field_key": "last_projected_year", "label_es": "Último año proyectado", "field_type": "number", "required": True},
    ],
    "technical_analysis": [{"field_key": "technical_analysis", "label_es": "Análisis técnico", "field_type": "table", "required": True}, {"field_key": "analysis", "label_es": "Descripción y requisitos del análisis técnico", "field_type": "textarea", "required": True}],
    "localization": [{"field_key": "localizations", "label_es": "Localización de la alternativa", "field_type": "table", "required": True}, {"field_key": "department", "label_es": "Departamento", "field_type": "select", "required": True}, {"field_key": "city", "label_es": "Municipio o ciudad", "field_type": "text", "required": True}, {"field_key": "coordinates", "label_es": "Coordenadas de la localización", "field_type": "text", "required": True}],
    "value_chain": [{"field_key": "value_chains", "label_es": "Cadena de valor", "field_type": "table", "required": True}, {"field_key": "value_chain_objectives", "label_es": "Objetivo específico de la cadena de valor", "field_type": "table", "required": True}, {"field_key": "products", "label_es": "Al menos un producto", "field_type": "table", "required": True}, {"field_key": "product_name", "label_es": "Nombre del producto", "field_type": "text", "required": True}, {"field_key": "activities", "label_es": "Actividades", "field_type": "table", "required": True}],
}


def get_section_field_catalog(section: str) -> List[Dict[str, Any]]:
    canonical = normalize_section(section)
    fields = []
    for field in _CATALOG.get(canonical, []):
        select_metadata = get_select_metadata(field["field_key"]) if field["field_type"] == "select" else None
        fields.append({
            **field,
            "section": canonical,
            "implemented": True,
            "allowed_values": (select_metadata or {}).get("allowed_values", field.get("allowed_values", [])),
        })
    return fields