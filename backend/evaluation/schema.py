"""Estructuras de datos del framework de evaluación."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Dict, List, Optional

# Variantes comparables. La ÚNICA diferencia entre ellas es el contexto
# disponible: mismo prompt general, mismo prompt de sección, misma pregunta,
# mismo historial, misma configuración de generación y mismo modelo.
VARIANTS = ("A", "B", "C")

VARIANT_DESCRIPTIONS = {
    "A": "solo pregunta + instrucciones del modelo/sección (project_context y rag_context vacíos)",
    "B": "pregunta + contexto estructurado del proyecto (rag_context vacío)",
    "C": "pregunta + contexto estructurado + contexto recuperado del Manual MGA 2015",
}

CASE_TYPES = ("review", "improve", "inconsistency", "incomplete")


@dataclass(frozen=True)
class ExpectedCriteria:
    """Criterios verificables de una respuesta correcta según MGA."""

    must: List[str]
    must_not: List[str] = field(default_factory=list)


@dataclass(frozen=True)
class EvaluationCase:
    """Un caso de prueba reproducible.

    `registered_data` es SOLO documentación legible del caso: nunca alimenta al
    LLM. El contexto real se construye siempre por el flujo de producción
    (fixture -> SQLAlchemy -> ContextLoaders -> ContextManager).
    """

    id: str
    section: str
    type: str
    fixture: str
    question: str
    expected: ExpectedCriteria
    registered_data: Dict[str, Any] = field(default_factory=dict)
    notes: str = ""


@dataclass
class TokenUsage:
    """Uso de tokens. `source` distingue conteo real de estimación."""

    source: str  # "provider" | "estimated_tiktoken"
    prompt: Optional[int] = None
    completion: Optional[int] = None
    total: Optional[int] = None
    method: str = ""

    def as_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class RunRecord:
    """Registro de una ejecución (caso × variante). Se serializa a JSONL."""

    run_id: str
    case_id: str
    section: str
    case_type: str
    variant: str
    executed: bool
    model: Dict[str, Any]
    config: Dict[str, Any]
    prompt: Dict[str, Any]
    response: Optional[str] = None
    timing: Dict[str, float] = field(default_factory=dict)
    tokens: Optional[Dict[str, Any]] = None
    error: Optional[Dict[str, str]] = None

    def as_dict(self) -> Dict[str, Any]:
        return asdict(self)
