"""Validación del dataset de evaluación. No invoca ningún proveedor LLM."""

from __future__ import annotations

from pathlib import Path

import pytest

from app.ai.context.module_dependencies import CANONICAL_SECTIONS
from evaluation.fixtures import FIXTURES, build_case_session
from evaluation.loader import CASES_DIR, CaseValidationError, load_cases, load_cases_by_section
from evaluation.runner import EMPTY_CHAT_HISTORY, _build_llm_manager, build_case_contexts, run_case
from evaluation.schema import CASE_TYPES, VARIANTS

EXPECTED_SECTIONS = {
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


@pytest.fixture(scope="module")
def cases():
    return load_cases()


@pytest.fixture(scope="module")
def dry_run_manager():
    return _build_llm_manager(execute=False)


# ---------------------------------------------------------------------------
# Dataset
# ---------------------------------------------------------------------------

def test_dataset_has_exactly_nine_initial_cases(cases):
    assert len(cases) == 9


def test_one_case_per_section(cases):
    sections = [case.section for case in cases]
    assert set(sections) == EXPECTED_SECTIONS
    assert len(sections) == len(set(sections))


def test_case_ids_are_unique(cases):
    ids = [case.id for case in cases]
    assert len(ids) == len(set(ids))


def test_sections_are_canonical(cases):
    assert all(case.section in CANONICAL_SECTIONS for case in cases)


def test_initial_cases_are_inconsistency_type(cases):
    assert all(case.type == "inconsistency" for case in cases)
    assert all(case.type in CASE_TYPES for case in cases)


def test_questions_are_not_empty(cases):
    assert all(case.question.strip() for case in cases)


def test_expected_must_is_not_empty_and_bounded(cases):
    for case in cases:
        assert case.expected.must
        assert 2 <= len(case.expected.must) <= 4
        assert 1 <= len(case.expected.must_not) <= 3


def test_every_case_references_an_existing_fixture(cases):
    assert all(case.fixture in FIXTURES for case in cases)


def test_loader_rejects_unknown_section(tmp_path):
    (tmp_path / "bad.yaml").write_text(
        "- id: x-01\n  section: seccion_inventada\n  type: inconsistency\n"
        "  fixture: problems_cause_as_missing_solution\n  question: q\n"
        "  expected:\n    must: ['algo']\n",
        encoding="utf-8",
    )
    with pytest.raises(CaseValidationError):
        load_cases(tmp_path)


def test_loader_rejects_empty_must(tmp_path):
    (tmp_path / "bad.yaml").write_text(
        "- id: x-01\n  section: problems\n  type: inconsistency\n"
        "  fixture: problems_cause_as_missing_solution\n  question: q\n"
        "  expected:\n    must: []\n",
        encoding="utf-8",
    )
    with pytest.raises(CaseValidationError):
        load_cases(tmp_path)


def test_filter_by_section(cases):
    filtered = load_cases_by_section(["problems"])
    assert len(filtered) == 1
    assert filtered[0].section == "problems"


# ---------------------------------------------------------------------------
# Fixtures y aislamiento
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("fixture_name", sorted(FIXTURES))
def test_fixture_seeds_successfully(fixture_name):
    db = build_case_session()
    try:
        project_id = FIXTURES[fixture_name](db)
        assert isinstance(project_id, int) and project_id > 0
    finally:
        db.close()


def test_cases_are_isolated_from_each_other():
    """El proyecto de un caso no contamina el de otro (BD independiente)."""
    from app.models.project import Project

    db_a = build_case_session()
    db_b = build_case_session()
    try:
        FIXTURES["problems_cause_as_missing_solution"](db_a)
        FIXTURES["value_chain_product_is_actually_activity"](db_b)

        assert db_a.query(Project).count() == 1
        assert db_b.query(Project).count() == 1

        from app.models.problems import Problems
        from app.models.value_chain import ValueChain

        assert db_a.query(ValueChain).count() == 0
        assert db_b.query(Problems).count() == 1  # el fixture de value_chain siembra su propio upstream
        assert db_a.query(Problems).count() == 1
    finally:
        db_a.close()
        db_b.close()


def test_planted_defect_reaches_the_generated_context(dry_run_manager, cases):
    """El defecto controlado debe ser visible en el contexto que verá el LLM."""
    markers = {
        "problems": "variante pavimentada",
        "participants": "artesanos",
        "population": "5000",
        "objectives": "internet",
        "alternatives": "mayor pendiente",
        "requirements": "Obras de drenaje construidas",
        "technical_analysis": "concreto asfáltico",
        "localization": "Atlántico",
        "value_chain": "interventoría técnica",
    }
    for case in cases:
        built = build_case_contexts(dry_run_manager, case)
        assert markers[case.section] in built["project_context"], case.id


# ---------------------------------------------------------------------------
# Dry-run y construcción A/B/C
# ---------------------------------------------------------------------------

@pytest.fixture(scope="module")
def problems_records(dry_run_manager):
    case = load_cases_by_section(["problems"])[0]
    return {r.variant: r for r in run_case(dry_run_manager, case, list(VARIANTS), "test-run", execute=False)}


@pytest.mark.parametrize("variant", VARIANTS)
def test_dry_run_builds_every_variant(problems_records, variant):
    record = problems_records[variant]
    assert record.prompt["full_prompt"]
    assert record.variant == variant


def test_variant_a_has_no_project_context_and_no_rag(problems_records):
    prompt = problems_records["A"].prompt
    assert prompt["project_context"] == ""
    assert prompt["rag_context"] == ""


def test_variant_b_has_project_context_but_no_rag(problems_records):
    prompt = problems_records["B"].prompt
    assert prompt["project_context"]
    assert prompt["rag_context"] == ""


def test_variant_c_has_both_contexts(problems_records):
    prompt = problems_records["C"].prompt
    assert prompt["project_context"]
    assert prompt["rag_context"]


def test_variant_b_and_c_share_the_same_project_context(problems_records):
    assert problems_records["B"].prompt["project_context"] == problems_records["C"].prompt["project_context"]


def test_question_is_identical_across_variants(problems_records):
    questions = {problems_records[v].prompt["question"] for v in VARIANTS}
    assert len(questions) == 1


def test_instructions_are_identical_across_variants(problems_records):
    """Mismo prompt general y mismo prompt de sección en A/B/C."""
    marker = "=== INFORMACIÓN REGISTRADA DEL PROYECTO ==="
    heads = {problems_records[v].prompt["full_prompt"].split(marker)[0] for v in VARIANTS}
    assert len(heads) == 1


def test_chat_history_is_empty_in_initial_cases(problems_records):
    assert EMPTY_CHAT_HISTORY == []
    assert all(problems_records[v].prompt["chat_history"] == "" for v in VARIANTS)


def test_dry_run_does_not_invoke_any_provider(problems_records):
    for variant in VARIANTS:
        record = problems_records[variant]
        assert record.executed is False
        assert record.response is None
        assert record.error is None


def test_dry_run_manager_has_no_initialized_model(dry_run_manager):
    assert dry_run_manager.model is None


def test_dry_run_tokens_are_marked_as_estimated(problems_records):
    for variant in VARIANTS:
        tokens = problems_records[variant].tokens
        assert tokens["source"] == "estimated_tiktoken"
        assert tokens["prompt"] > 0


def test_token_count_grows_with_available_context(problems_records):
    a, b, c = (problems_records[v].tokens["prompt"] for v in VARIANTS)
    assert a < b < c


def test_run_record_traces_the_rag_corpus(problems_records):
    config = problems_records["C"].config
    assert config["source_document"] == "Documento_conceptual_2023.pdf"
    assert config["index_hash"]


def test_registered_data_is_documentation_only(cases):
    """El YAML documenta el caso; el contexto real proviene de la BD."""
    for case in cases:
        assert isinstance(case.registered_data, dict)


def test_case_files_exist_one_per_section():
    files = {path.stem for path in CASES_DIR.glob("*.yaml")}
    assert files == EXPECTED_SECTIONS
