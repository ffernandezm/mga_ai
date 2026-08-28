"""Términos de dominio por sección MGA para enriquecer la consulta de retrieval.

Se usan EXCLUSIVAMENTE para construir la query del RAG. La pregunta original
del usuario nunca se modifica: llega intacta al LLM.

Motivo: preguntas vagas ("¿Qué me falta?", "¿Esto está bien?") no contienen
términos metodológicos y recuperaban 0-1 chunks. Con los términos de sección
recuperan el capítulo correcto del manual.
"""

from __future__ import annotations

SECTION_QUERY_TERMS: dict[str, str] = {
    "development_plans": "plan de desarrollo politica publica Plan Nacional de Desarrollo",
    "problems": "problematica arbol de problemas problema central causas efectos",
    "participants": "participantes actores intereses roles contribuciones conflictos",
    "population": "poblacion afectada poblacion objetivo caracterizacion",
    "objectives": "arbol de objetivos objetivo general objetivos especificos medios fines",
    "alternatives": "alternativas de solucion acciones medios objetivos",
    "requirements": "estudio de necesidades oferta demanda deficit bienes servicios",
    "technical_analysis": "analisis tecnico alternativa caracteristicas tecnicas capacidad",
    "localization": "localizacion alternativa poblacion objetivo factores localizacion",
    "value_chain": "cadena de valor objetivos productos actividades costos",
}


def build_retrieval_query(question: str, section: str | None = None) -> str:
    """Antepone los términos de la sección a la pregunta, solo para retrieval."""
    terms = SECTION_QUERY_TERMS.get((section or "").strip().lower())
    if not terms:
        return question
    return f"{terms} {question}"
