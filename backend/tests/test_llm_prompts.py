"""Tests de auditoría de prompts, templates, tokens y contexto incompleto.

Cubre: claves canónicas de templates, question/RAG únicos, aliases legados,
ausencia de variables faltantes al formatear, comportamiento con contexto
incompleto (sin inventar datos), y la utilidad de medición de tokens.
"""

from __future__ import annotations

import pytest

from app.ai.context.context_manager import ContextManager, render_semantic_context
from app.ai.llm_models.llm_manager import LLMManager
from app.ai.llm_models.token_diagnostics import PromptTokenReport, count_tokens
from app.models.alternatives_general import AlternativesGeneral
from app.models.alternatives import Alternatives
from app.models.objectives import Objectives
from app.models.problems import Problems
from app.models.project import Project
from app.models.requirements_general import RequirementsGeneral

from test_chat_integration import _make_test_llm_manager
from test_context_loaders import _seed_project


CANONICAL_SECTIONS = [
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
]

LEGACY_ALIASES = {
    "participants_general": "participants",
    "alternatives_general": "alternatives",
    "requirements_general": "requirements",
    "localization_general": "localization",
}


@pytest.fixture()
def manager():
    return _make_test_llm_manager()


# ---------------------------------------------------------------------------
# Templates canónicos
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("section", CANONICAL_SECTIONS)
def test_canonical_section_has_own_template_content(manager, section):
    assert section in manager.templates
    assert manager.templates[section].strip()


def test_general_and_default_templates_exist(manager):
    assert manager.templates.get("general", "").strip()
    assert manager.templates.get("default", "").strip()


# ---------------------------------------------------------------------------
# Aliases de prompts (legados -> canónico)
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("legacy_tab,canonical", LEGACY_ALIASES.items())
def test_legacy_tab_alias_resolves_to_canonical_prompt(manager, legacy_tab, canonical):
    legacy_prompt = manager.get_prompt_template(legacy_tab)
    canonical_prompt = manager.get_prompt_template(canonical)
    assert legacy_prompt.template == canonical_prompt.template


# ---------------------------------------------------------------------------
# Ausencia de variables faltantes en templates (format sin KeyError)
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("section", CANONICAL_SECTIONS + ["general", "default"])
def test_prompt_template_formats_without_missing_variables(manager, section):
    prompt = manager.get_prompt_template(section)
    # No debe lanzar KeyError por llaves { } sueltas dentro del contenido del template.
    rendered = prompt.format(
        project_context="CTX PROYECTO",
        rag_context="CTX RAG",
        chat_history="CTX HISTORIAL",
        question="¿Pregunta?",
    )
    assert "CTX PROYECTO" in rendered
    assert "CTX RAG" in rendered
    assert "¿Pregunta?" in rendered


# ---------------------------------------------------------------------------
# Question / RAG exactamente una vez (a nivel unitario, sin BD)
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("section", CANONICAL_SECTIONS)
def test_question_and_rag_appear_exactly_once(manager, section):
    question = "¿Esta sección está bien formulada?"
    rag_text = "[DOC MGA] fragmento único recuperado."
    manager.rag_manager.get_relevant_context = lambda q, section=None: rag_text

    full_prompt = manager.ask(question=question, tab=section, context="Datos de proyecto X", chat_history=None)

    assert full_prompt.count(question) == 1
    assert full_prompt.count(rag_text) == 1


# ---------------------------------------------------------------------------
# Renderer: encabezados presentes/ausentes según contenido
# ---------------------------------------------------------------------------

def test_renderer_omits_empty_blocks():
    empty_context = {"section": "problems", "current": {}, "required": {}, "supporting": {}}
    rendered = render_semantic_context(empty_context)
    assert "INFORMACIÓN GENERAL DEL PROYECTO" not in rendered
    assert "No hay contexto registrado relevante" in rendered


def test_renderer_shows_only_populated_blocks():
    context = {
        "section": "problems",
        "current": {"problem_tree": {"central_problem": "Problema X"}},
        "required": {"project": {"name": "Proyecto X"}},
        "supporting": {},
    }
    rendered = render_semantic_context(context)
    assert "=== INFORMACIÓN GENERAL DEL PROYECTO ===" in rendered
    assert "=== INFORMACIÓN REGISTRADA EN LA SECCIÓN ACTUAL ===" in rendered
    assert "=== CONTEXTO RELACIONADO DE LA FORMULACIÓN ===" not in rendered  # solo "project", ya usado arriba


# ---------------------------------------------------------------------------
# Contexto incompleto: no se inventa, no se rompe
# ---------------------------------------------------------------------------

def test_objectives_without_problem_tree_does_not_crash_or_invent(db_session):
    project = Project(name="Proyecto sin problema")
    db_session.add(project)
    db_session.flush()
    db_session.add(Objectives(project_id=project.id, general_objective="Objetivo sin problema previo"))
    db_session.commit()

    cm = ContextManager()
    context = cm.build_semantic_context(db=db_session, project_id=project.id, section="objectives")
    assert context["current"]["objectives"]["general_objective"] == "Objetivo sin problema previo"
    assert context["required"]["problem_tree"] == {}
    rendered = render_semantic_context(context)
    assert "ÁRBOL DE PROBLEMAS" not in rendered  # bloque vacío omitido, no inventado


def test_requirements_without_selected_alternative(db_session):
    project = Project(name="Proyecto sin alternativa")
    db_session.add(project)
    db_session.flush()
    db_session.add(RequirementsGeneral(project_id=project.id, requirements_analysis="Analisis sin alternativa"))
    db_session.commit()

    cm = ContextManager()
    context = cm.build_semantic_context(db=db_session, project_id=project.id, section="requirements")
    assert context["required"]["selected_alternative"] == {}
    rendered = render_semantic_context(context)
    assert "ALTERNATIVA SELECCIONADA" not in rendered


def test_technical_analysis_without_requirements(db_session):
    project = Project(name="Proyecto sin requerimientos")
    db_session.add(project)
    db_session.commit()

    cm = ContextManager()
    context = cm.build_semantic_context(db=db_session, project_id=project.id, section="technical_analysis")
    assert context["required"]["requirements"] == {}
    assert context["current"]["technical_analysis"] == {}


def test_localization_without_population(db_session):
    from app.models.localization_general import LocalizationGeneral

    project = Project(name="Proyecto sin poblacion")
    db_session.add(project)
    db_session.flush()
    db_session.add(LocalizationGeneral(project_id=project.id, proximity_to_target_population=True))
    db_session.commit()

    cm = ContextManager()
    context = cm.build_semantic_context(db=db_session, project_id=project.id, section="localization")
    assert context["required"]["intervention_population"] == {}
    assert "Proximidad a la población objetivo" in context["current"]["localization"]["active_factors"]


def test_value_chain_without_objectives(db_session):
    from app.models.value_chain import ValueChain

    project = Project(name="Proyecto sin objetivos")
    db_session.add(project)
    db_session.flush()
    db_session.add(ValueChain(project_id=project.id, name="Cadena huerfana"))
    db_session.commit()

    cm = ContextManager()
    context = cm.build_semantic_context(db=db_session, project_id=project.id, section="value_chain")
    assert context["required"]["objectives"] == {}
    assert context["current"]["value_chain"]["name"] == "Cadena huerfana"


# ---------------------------------------------------------------------------
# Política de no invención (declarada en el prompt de sistema/secciones)
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("section", CANONICAL_SECTIONS)
def test_no_invention_policy_present_in_general_or_section_prompt(manager, section):
    general = manager.templates.get("general", "").lower()
    assert "no inventes" in general


# ---------------------------------------------------------------------------
# Medición de tokens
# ---------------------------------------------------------------------------

def test_count_tokens_basic():
    assert count_tokens("") == 0
    assert count_tokens("hola mundo") > 0


def test_measure_prompt_tokens_structure(manager, db_session):
    project_id = _seed_project(db_session, "T")
    cm = ContextManager()
    context = cm.build_semantic_context(db=db_session, project_id=project_id, section="problems")
    rendered = render_semantic_context(context)

    report = manager.measure_prompt_tokens(question="¿Cuál es el problema?", tab="problems", context=rendered)
    assert isinstance(report, PromptTokenReport)
    d = report.as_dict()
    for key in (
        "section",
        "system_tokens",
        "project_context_tokens",
        "rag_context_tokens",
        "history_tokens",
        "question_tokens",
        "estimated_total_tokens",
        "token_method",
    ):
        assert key in d
    assert d["estimated_total_tokens"] == (
        d["system_tokens"] + d["project_context_tokens"] + d["rag_context_tokens"] + d["history_tokens"] + d["question_tokens"]
    )
    assert d["project_context_tokens"] > 0


def test_measure_prompt_tokens_history_bounded_regardless_of_length(manager):
    long_history = [{"sender": "user", "message": "x" * 400} for _ in range(50)]
    short_history = [{"sender": "user", "message": "x" * 400} for _ in range(6)]

    report_long = manager.measure_prompt_tokens(question="q", tab="problems", context="", chat_history=long_history)
    report_short = manager.measure_prompt_tokens(question="q", tab="problems", context="", chat_history=short_history)

    # El historial usado en el prompt está acotado por max_chat_history_messages,
    # independientemente de cuántos mensajes existan en la conversación.
    assert report_long.history_tokens == report_short.history_tokens
