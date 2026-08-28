"""Carga y validación del dataset de casos de evaluación."""

from __future__ import annotations

from pathlib import Path
from typing import Dict, List

import yaml

from app.ai.context.module_dependencies import CANONICAL_SECTIONS

from .fixtures import FIXTURES
from .schema import CASE_TYPES, EvaluationCase, ExpectedCriteria

CASES_DIR = Path(__file__).resolve().parent / "cases"


class CaseValidationError(ValueError):
    """El dataset de casos es inválido."""


def _parse_case(raw: Dict, source: Path) -> EvaluationCase:
    missing = [key for key in ("id", "section", "type", "fixture", "question", "expected") if key not in raw]
    if missing:
        raise CaseValidationError(f"{source.name}: faltan campos {missing}")

    expected = raw["expected"] or {}
    must = expected.get("must") or []
    if not must:
        raise CaseValidationError(f"{raw['id']}: 'expected.must' no puede estar vacío")

    if raw["section"] not in CANONICAL_SECTIONS:
        raise CaseValidationError(f"{raw['id']}: sección '{raw['section']}' no es canónica")
    if raw["type"] not in CASE_TYPES:
        raise CaseValidationError(f"{raw['id']}: tipo '{raw['type']}' no válido")
    if raw["fixture"] not in FIXTURES:
        raise CaseValidationError(f"{raw['id']}: fixture '{raw['fixture']}' no existe")
    if not str(raw["question"]).strip():
        raise CaseValidationError(f"{raw['id']}: 'question' no puede estar vacía")

    return EvaluationCase(
        id=raw["id"],
        section=raw["section"],
        type=raw["type"],
        fixture=raw["fixture"],
        question=raw["question"],
        expected=ExpectedCriteria(must=list(must), must_not=list(expected.get("must_not") or [])),
        registered_data=raw.get("registered_data") or {},
        notes=raw.get("notes", "") or "",
    )


def load_cases(cases_dir: Path | None = None) -> List[EvaluationCase]:
    """Carga todos los casos y valida ids únicos y campos obligatorios."""
    directory = cases_dir or CASES_DIR
    cases: List[EvaluationCase] = []

    for path in sorted(directory.glob("*.yaml")):
        payload = yaml.safe_load(path.read_text(encoding="utf-8")) or []
        if not isinstance(payload, list):
            raise CaseValidationError(f"{path.name}: se esperaba una lista de casos")
        cases.extend(_parse_case(raw, path) for raw in payload)

    seen: Dict[str, str] = {}
    for case in cases:
        if case.id in seen:
            raise CaseValidationError(f"id duplicado: {case.id}")
        seen[case.id] = case.section

    return cases


def load_cases_by_section(sections: List[str] | None = None) -> List[EvaluationCase]:
    cases = load_cases()
    if not sections:
        return cases
    wanted = {s.strip().lower() for s in sections}
    return [case for case in cases if case.section in wanted]
