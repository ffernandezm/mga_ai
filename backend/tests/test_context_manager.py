import pytest

from app.ai.context.context_manager import ContextManager


@pytest.fixture
def context_manager():
    return ContextManager()


def test_problems_generation_context_excludes_downstream_sections(context_manager):
    context = context_manager.build_context(
        project_id=1,
        section="problems",
        mode="generation",
        project_data={
            "project": {"name": "Proyecto X"},
            "planning_alignment": {"national_plan": "Plan de Desarrollo"},
            "problem_tree": {
                "central_problem": "Falta de acceso",
                "direct_causes": [{"description": "Bajo presupuesto"}],
                "direct_effects": [{"description": "Inequidad"}],
            },
            "objectives": {"general_objective": "Objetivo largo"},
            "alternatives": [{"name": "Alternativa A"}],
            "value_chain": {"name": "Cadena"},
        },
    )

    assert "PROYECTO" in context
    assert "Plan de Desarrollo" in context
    assert "Falta de acceso" in context
    assert "Objetivo largo" not in context
    assert "Alternativa A" not in context
    assert "Cadena" not in context


def test_objectives_generation_context_uses_problem_tree_and_planning(context_manager):
    context = context_manager.build_context(
        project_id=1,
        section="objectives",
        mode="generation",
        project_data={
            "project": {"name": "Proyecto X"},
            "planning_alignment": {"national_plan": "Plan N"},
            "problem_tree": {
                "central_problem": "Problema central",
                "direct_causes": [{"description": "Causa 1"}],
                "indirect_causes": [{"description": "Causa indirecta"}],
                "direct_effects": [{"description": "Efecto 1"}],
                "indirect_effects": [{"description": "Efecto indirecto"}],
            },
        },
    )

    assert "Problema central" in context
    assert "Causa 1" in context
    assert "Causa indirecta" in context
    assert "Efecto indirecto" in context
    assert "Plan N" in context


def test_alternatives_context_includes_objectives_and_supporting_summary(context_manager):
    context = context_manager.build_context(
        project_id=1,
        section="alternatives",
        mode="generation",
        project_data={
            "project": {"name": "Proyecto X"},
            "objectives": {"general_objective": "Objetivo general"},
            "problem_summary": {"central_problem": "Problema"},
            "population_summary": {"population_type_intervention": "Población"},
            "participants_summary": {"actors": ["Actor 1"]},
        },
    )

    assert "Objetivo general" in context
    assert "Problema" in context
    assert "Población" in context
    assert "Actor 1" in context


def test_context_omits_internal_ids_and_empty_values(context_manager):
    context = context_manager.build_context(
        project_id=1,
        section="technical_analysis",
        mode="generation",
        project_data={
            "project": {"name": "Proyecto X"},
            "selected_alternative": {"name": "Alternativa principal"},
            "requirements": [{"good_service_name": "Servicio", "supply_description": "Oferta"}],
            "technical_analysis": {"analysis": "Análisis técnico"},
            "empty": None,
            "internal_id": 999,
        },
    )

    assert "Alternativa principal" in context
    assert "Servicio" in context
    assert "analysis" not in context.lower() or "Análisis técnico" in context
    assert "internal_id" not in context
    assert "999" not in context


def test_prompt_context_keeps_question_single_and_no_duplicate_json(context_manager):
    builder = context_manager
    prompt_context = builder.build_prompt_payload(
        section="problems",
        mode="generation",
        question="Evalúa el problema central",
        project_data={
            "project": {"name": "Proyecto"},
            "planning_alignment": {"national_plan": "Plan"},
            "problem_tree": {"central_problem": "Problema"},
            "problem_tree_json": {"central_problem": "Problema duplicado"},
        },
    )

    assert prompt_context["question"] == "Evalúa el problema central"
    assert "problem_tree_json" not in prompt_context["project_context"].lower()
    assert "Problema duplicado" not in prompt_context["project_context"]
