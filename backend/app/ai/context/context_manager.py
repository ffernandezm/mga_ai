"""Context builder selectivo para prompts MGA."""

from __future__ import annotations

import logging
from collections.abc import Sequence
from typing import Any, Dict, Iterable, List, Optional, Tuple

from sqlalchemy.orm import Session

from .module_dependencies import (
    UnknownSectionError,
    get_forbidden_sections,
    get_section_current,
    get_section_dependencies,
    normalize_section,
)

logger = logging.getLogger(__name__)


_INTERNAL_KEYS = {"id", "project_id", "problem_id", "direct_cause_id", "direct_effect_id", "population_id", "objective_id", "cause_id", "value_chain_id", "value_chain_objective_id", "product_id", "requirements_general_id", "localization_general_id", "participants_general_id", "development_plan_id", "alternative_id", "source_id", "plan_id", "pillar_id", "strategy_id", "component_id"}

_FIELD_LABELS = {
    "name": "Nombre", "select_fields": "Campos de selección",
    "central_problem": "Problema central", "current_description": "Descripción de la situación existente", "magnitude_problem": "Magnitud del problema",
    "direct_causes": "Causas directas", "indirect_causes": "Causas indirectas", "direct_effects": "Efectos directos", "indirect_effects": "Efectos indirectos",
    "participants_analisis": "Análisis de los participantes", "participants_analysis": "Análisis de los participantes", "participant_actor": "Actor", "participant_entity": "Entidad", "interest_expectative": "Intereses y expectativas", "rol": "Rol", "contribution_conflicts": "Contribuciones o conflictos",
    "general_problem": "Problema central", "general_objective": "Objetivo general", "specifics_objectives": "Objetivos específicos", "objectives_causes": "Objetivos específicos", "objectives_indicators": "Indicadores de resultado",
    "requirements_analysis": "Análisis de necesidades", "goods_services": "Bienes y servicios", "good_service_name": "Bien o servicio", "supply_description": "Información de oferta", "demand_description": "Información de demanda", "unit_of_measure": "Unidad de medida",
    "administrative_level": "Nivel territorial", "department": "Departamento", "city": "Municipio", "value_chain": "Cadena de valor", "activities": "Actividades", "products": "Productos",
}


class ContextManager:
    """Genera un contexto semántico y selectivo para cada sección MGA."""

    def __init__(self):
        self.section_dependencies = get_section_dependencies

    @staticmethod
    def sanitize_context_text(value: str) -> str:
        cleaned = (value or "").strip()
        cleaned = cleaned.replace("\r\n", "\n")
        cleaned = cleaned.replace("\t", " ")
        cleaned = cleaned.replace("\u00a0", " ")
        cleaned = cleaned.replace("\n\n\n", "\n\n")
        return cleaned.strip()

    def build_context(
        self,
        db: Session | None = None,
        project_id: int | None = None,
        section: str = "general",
        mode: str = "generation",
        project_data: Dict[str, Any] | None = None,
    ):
        """Construye contexto para una sección MGA.

        API estable/nueva: usar `build_semantic_context(db, project_id, section, mode)`
        directamente cuando se disponga de una sesión de BD (ese es el contrato
        que debe usar el flujo de producción, p. ej. el endpoint de chat).

        Este método (`build_context`) se conserva únicamente por
        compatibilidad con el path legado (`project_data` ya construido
        externamente, sin `db`) y con los tests existentes. Si se pasa `db`,
        delega en `build_semantic_context` sin agregar comportamiento nuevo.

        - Si se pasa `db`, consulta PostgreSQL vía SEMANTIC_LOADERS y devuelve
          una estructura dict (ver `build_semantic_context`).
        - Si no, mantiene el comportamiento legado (DEPRECADO para flujos
          nuevos): recibe `project_data` ya construido externamente y
          devuelve un string renderizado.
        """
        if db is not None:
            return self.build_semantic_context(db=db, project_id=project_id, section=section, mode=mode)
        return self._build_context_from_data(project_id=project_id, section=section, mode=mode, project_data=project_data)

    def _build_context_from_data(self, project_id: int | None, section: str, mode: str, project_data: Dict[str, Any] | None) -> str:
        project_data = project_data or {}
        deps = self.section_dependencies(section, mode)
        sections = []

        for block_name in deps["required"] + deps["supporting"]:
            value = project_data.get(block_name)
            if value is None:
                continue
            rendered = self._render_semantic_block(block_name, value)
            if rendered:
                sections.append(rendered)

        title = "=== CONTEXTO SELECTIVO MGA ==="
        if not sections:
            return f"{title}\n\n(No hay contexto registrado relevante para la sección '{section}'.)"
        return f"{title}\n\n" + "\n\n".join(sections)

    def build_semantic_context(
        self,
        db: Session,
        project_id: Optional[int],
        section: str = "general",
        mode: str = "generation",
    ) -> Dict[str, Any]:
        """Construye el contexto real consultando la BD mediante SEMANTIC_LOADERS.

        Devuelve una estructura testeable (no convertida a string):
            {"section": ..., "current": {...}, "required": {...}, "supporting": {...}}
        """
        # Import diferido: context_loaders importa app.models.*, que a su vez
        # importa app.models.chat_history -> LLMManager -> ContextManager,
        # generando un ciclo si se importa a nivel de módulo.
        from .context_loaders import SEMANTIC_LOADERS

        try:
            canonical_section = normalize_section(section)
        except UnknownSectionError:
            logger.warning("Sección/tab desconocida '%s'; usando 'default'", section)
            canonical_section = "default"

        current_name = get_section_current(canonical_section)
        deps = get_section_dependencies(canonical_section, mode)
        required_names = [name for name in deps["required"] if name != current_name]
        supporting_names = [name for name in deps["supporting"] if name != current_name]

        cache: Dict[str, Any] = {}

        def _load(name: str) -> Any:
            if name in cache:
                return cache[name]
            loader = SEMANTIC_LOADERS.get(name)
            if not loader:
                cache[name] = {}
                return {}
            value = loader(db, project_id, cache)
            cache[name] = value
            return value

        current_obj = _load(current_name) if current_name else {}
        required_obj = {name: _load(name) for name in required_names}
        supporting_obj = {name: _load(name) for name in supporting_names}

        return {
            "section": canonical_section,
            "current": {current_name: current_obj} if current_name else {},
            "required": required_obj,
            "supporting": supporting_obj,
        }

    def build_prompt_payload(self, section: str, mode: str, question: str, project_data: Dict[str, Any] | None = None, chat_history: str = "", rag_context: str = "") -> Dict[str, str]:
        context_text = self.build_context(section=section, mode=mode, project_data=project_data)
        return {
            "project_context": context_text,
            "chat_history": chat_history or "",
            "rag_context": rag_context or "",
            "question": question,
        }

    def render_semantic_context(self, context: Dict[str, Any]) -> str:
        """Renderiza a texto el dict producido por `build_semantic_context`.

        Genera 3 bloques claramente identificables (sin exponer los términos
        técnicos "required"/"supporting" al LLM), omitiendo bloques vacíos,
        valores nulos, ids y snapshots JSON (ya excluidos por los loaders):

            === INFORMACIÓN GENERAL DEL PROYECTO ===
            === INFORMACIÓN REGISTRADA EN LA SECCIÓN ACTUAL ===
            === CONTEXTO RELACIONADO DE LA FORMULACIÓN ===

        NO incluye contexto RAG: eso es responsabilidad de RAGManager y se
        inserta en el prompt bajo una etiqueta separada (ver LLMManager).
        """
        required = context.get("required", {}) or {}
        supporting = context.get("supporting", {}) or {}
        current = context.get("current", {}) or {}

        blocks: List[str] = []

        project_value = required.get("project") or current.get("project")
        project_block = self._render_semantic_block("project", project_value) if project_value else ""
        if project_block:
            blocks.append("=== INFORMACIÓN GENERAL DEL PROYECTO ===\n\n" + project_block)

        current_rendered = []
        for name, value in current.items():
            if name == "project":
                continue
            rendered = self._render_semantic_block(name, value)
            if rendered:
                current_rendered.append(rendered)
        if current_rendered:
            blocks.append("=== INFORMACIÓN REGISTRADA EN LA SECCIÓN ACTUAL ===\n\n" + "\n\n".join(current_rendered))

        related_rendered: List[str] = []
        seen: set = set()
        for group in (required, supporting):
            for name, value in group.items():
                if name == "project":
                    continue
                rendered = self._render_semantic_block(name, value)
                if rendered and rendered not in seen:
                    related_rendered.append(rendered)
                    seen.add(rendered)
        if related_rendered:
            blocks.append("=== CONTEXTO RELACIONADO DE LA FORMULACIÓN ===\n\n" + "\n\n".join(related_rendered))

        if not blocks:
            section = context.get("section", "general")
            return f"(No hay contexto registrado relevante para la sección '{section}'.)"
        return "\n\n".join(blocks)

    def _render_semantic_block(self, block_name: str, value: Any) -> str:
        if value in (None, "", [], {}, False):
            return ""

        if block_name == "project":
            title = "PROYECTO"
            return self._render_mapping(title, value)
        if block_name == "planning_alignment":
            return self._render_mapping("ALINEACIÓN CON PLANES Y POLÍTICAS", value)
        if block_name == "problem_tree":
            return self._render_mapping("ÁRBOL DE PROBLEMAS", value)
        if block_name == "problem_summary":
            return self._render_mapping("RESUMEN DEL PROBLEMA", value)
        if block_name == "participants_summary":
            return self._render_mapping("RESUMEN DE PARTICIPANTES", value)
        if block_name == "population_summary":
            return self._render_mapping("RESUMEN DE POBLACIÓN", value)
        if block_name == "objectives":
            return self._render_mapping("OBJETIVOS", value)
        if block_name == "objectives_summary":
            return self._render_mapping("RESUMEN DE OBJETIVOS", value)
        if block_name == "alternatives":
            return self._render_list("ALTERNATIVAS REGISTRADAS", value)
        if block_name == "selected_alternative":
            return self._render_selected_alternative(value)
        if block_name == "requirements":
            # load_requirements devuelve un dict {"requirements_analysis", "goods_services": [...]}.
            # Se mantiene compatibilidad con el path legado (project_data), que
            # históricamente pasaba directamente una lista de bienes/servicios.
            if isinstance(value, list):
                return self._render_list("REQUERIMIENTOS", value)
            return self._render_mapping("REQUERIMIENTOS", value)
        if block_name == "technical_analysis":
            return self._render_mapping("ANÁLISIS TÉCNICO", value)
        if block_name == "intervention_population":
            return self._render_mapping("POBLACIÓN DE INTERVENCIÓN", value)
        if block_name == "selected_product_catalogs":
            return self._render_list("CATÁLOGOS DE PRODUCTOS SELECCIONADOS", value)
        if block_name == "value_chain":
            return self._render_mapping("CADENA DE VALOR", value)
        return self._render_mapping(block_name.upper().replace("_", " "), value)

    def _render_selected_alternative(self, value: Dict[str, Any]) -> str:
        """Maneja explícitamente el caso de inconsistencia (>1 alternativa activa).

        No se elige una alternativa en silencio: se informa la ambigüedad al LLM
        en vez de fingir que hay una selección clara.
        """
        return self._render_mapping("ALTERNATIVAS DISPONIBLES", value)

    def _render_mapping(self, title: str, payload: Dict[str, Any]) -> str:
        lines = [f"[{title}]"]
        for key, value in self._iter_clean_items(payload):
            if key == "Campos de selección" and isinstance(value, list):
                lines.extend(self._render_select_domains(value))
                continue
            if isinstance(value, (dict, list)):
                nested = self._format_nested(key, value)
                if nested:
                    lines.append(f"- {key}: {nested}")
            else:
                clean_value = self._clean_scalar(value)
                if clean_value:
                    lines.append(f"- {key}: {clean_value}")
        return "\n".join(lines) if len(lines) > 1 else ""

    def _render_select_domains(self, fields: List[Dict[str, Any]]) -> List[str]:
        lines = ["- Campos de selección permitidos:"]
        for field in fields:
            values = field.get("allowed_values", [])
            labels = [item.get("label", item.get("value", "")) for item in values]
            lines.append(f"  - {field.get('label_es', field.get('field_key'))} [{field.get('field_key')}]: {', '.join(labels)}")
        lines.append("  - Solo propone valores exactamente incluidos en estas opciones. Si no hay equivalencia, indícalo explícitamente sin inventar una opción.")
        return lines

    def _render_list(self, title: str, payload: Any) -> str:
        if not isinstance(payload, list) or not payload:
            return ""

        lines = [f"[{title}]"]
        for idx, item in enumerate(payload, 1):
            if isinstance(item, dict):
                item_lines = []
                for key, value in self._iter_clean_items(item):
                    clean_value = self._clean_scalar(value)
                    if clean_value:
                        item_lines.append(f"{key}: {clean_value}")
                if item_lines:
                    lines.append(f"{idx}. {', '.join(item_lines)}")
            else:
                clean_value = self._clean_scalar(item)
                if clean_value:
                    lines.append(f"{idx}. {clean_value}")
        return "\n".join(lines) if len(lines) > 1 else ""

    def _iter_clean_items(self, payload: Dict[str, Any]) -> Iterable[Tuple[str, Any]]:
        if not isinstance(payload, dict):
            return []

        cleaned: List[Tuple[str, Any]] = []
        for key, value in payload.items():
            if self._should_skip_key(key, value):
                continue
            cleaned.append((self._readable_key(key), value))
        return cleaned

    def _should_skip_key(self, key: str, value: Any) -> bool:
        normalized = str(key).lower()
        if normalized in _INTERNAL_KEYS or normalized.endswith("_id"):
            return True
        if normalized == "id":
            return True
        if "json" in normalized:
            return True
        if value is None:
            return True
        if isinstance(value, str) and not value.strip():
            return True
        if isinstance(value, (list, dict)) and not value:
            return True
        return False

    def _readable_key(self, key: str) -> str:
        if key in _FIELD_LABELS:
            return _FIELD_LABELS[key]
        cleaned = str(key).replace("_", " ").strip()
        return cleaned.title()

    def _format_nested(self, key: str, value: Any) -> str:
        """Renderiza dict/list anidados de forma recursiva (profundidad arbitraria).

        Necesario para jerarquías de 3+ niveles como
        value_chain -> objectives -> products -> activities: sin recursión,
        el nivel más profundo caía a `str(value)` (repr crudo tipo JSON).
        """
        if isinstance(value, list):
            parts = []
            for item in value:
                if isinstance(item, dict):
                    compact = self._format_item_compact(item)
                    if compact:
                        parts.append(compact)
                elif isinstance(item, list):
                    nested = self._format_nested(key, item)
                    if nested:
                        parts.append(nested)
                else:
                    scalar = self._clean_scalar(item)
                    if scalar:
                        parts.append(scalar)
            return "; ".join(parts) if parts else ""

        if isinstance(value, dict):
            return self._format_item_compact(value)

        scalar = self._clean_scalar(value)
        return scalar or ""

    def _format_item_compact(self, item: Dict[str, Any]) -> str:
        parts = []
        for key, value in self._iter_clean_items(item):
            if isinstance(value, (list, dict)):
                nested = self._format_nested(key, value)
                if nested:
                    parts.append(f"{key} ({nested})")
            else:
                scalar = self._clean_scalar(value)
                if scalar:
                    parts.append(f"{key}: {scalar}")
        return ", ".join(parts) if parts else ""

    def _clean_scalar(self, value: Any) -> str:
        if value is None:
            return ""
        if isinstance(value, bool):
            return "Sí" if value else "No"
        if isinstance(value, (int, float)):
            return str(value)
        if isinstance(value, str):
            cleaned = value.strip()
            return cleaned[:250] if cleaned else ""
        return str(value)[:250]


def render_semantic_context(context: Dict[str, Any]) -> str:
    """Función de conveniencia: renderiza el dict de `build_semantic_context` a texto.

    Equivalente a `ContextManager().render_semantic_context(context)`. Es el
    renderer que debe usar el flujo de producción (endpoint de chat) para
    convertir el contexto semántico en el string que recibe `LLMManager`.
    """
    return ContextManager().render_semantic_context(context)
