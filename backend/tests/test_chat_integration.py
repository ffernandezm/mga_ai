"""Tests de integración: endpoint /chat_history/chat -> ContextManager -> LLMManager.

Se llama a `chat_with_ai(...)` directamente como función Python (sin capa HTTP)
para poder inyectar una sesión SQLite en memoria y mockear LLM/RAG sin
depender de credenciales externas.
"""

from __future__ import annotations

from types import SimpleNamespace

import pytest
from langchain_core.runnables import Runnable

import app.models.chat_history as chat_history_module
from app.ai.context.context_manager import ContextManager
from app.ai.llm_models.llm_manager import LLMManager
from app.models.alternatives import Alternatives
from app.models.alternatives_general import AlternativesGeneral
from app.models.project import Project

from test_context_loaders import _seed_global_tables, _seed_project


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

class _EchoModel(Runnable):
    """Modelo LLM falso: devuelve el prompt ya renderizado (para poder inspeccionarlo)."""

    def invoke(self, input, config=None, **kwargs):
        return input.to_string() if hasattr(input, "to_string") else str(input)


def _make_test_llm_manager(rag_text: str = "[DOC MGA] contenido metodológico recuperado del PDF."):
    """Construye un LLMManager real (mismos templates/ContextManager) sin llamar a proveedores externos."""
    manager = LLMManager.__new__(LLMManager)
    manager.llm_provider = "test"
    manager.templates = manager._load_templates()
    manager.rag_manager = SimpleNamespace(get_relevant_context=lambda q, section=None: rag_text)
    manager.context_manager = ContextManager()
    manager.max_chat_history_messages = 6
    manager.max_project_context_chars = 12000
    manager.model = _EchoModel()
    manager._is_invoke_skipped = lambda: False
    return manager


@pytest.fixture()
def fake_llm_capture(monkeypatch):
    """Reemplaza el `llm_manager.ask` global del endpoint por uno que solo captura argumentos."""
    calls = []

    def _fake_ask(question, tab="general", context="", chat_history=None, session_id=None):
        calls.append({"question": question, "tab": tab, "context": context, "chat_history": chat_history})
        return f"[FAKE-ANSWER] {question}"

    monkeypatch.setattr(chat_history_module.llm_manager, "ask", _fake_ask)
    return calls


@pytest.fixture(autouse=True)
def completed_chat_prerequisites(monkeypatch):
    """Estas pruebas cubren el payload LLM; el bloqueo upstream se prueba aparte."""
    monkeypatch.setattr(
        chat_history_module.SectionValidationService,
        "validate_section",
        lambda self, project_id, section: SimpleNamespace(
            prerequisites_complete=True,
            incomplete_prerequisites=[],
        ),
    )


# ---------------------------------------------------------------------------
# 1-2. Endpoint problems: usa contexto semántico, no incluye downstream
# ---------------------------------------------------------------------------

def test_endpoint_problems_uses_semantic_context_and_excludes_downstream(db_session, fake_llm_capture):
    _seed_global_tables(db_session)
    project_a = _seed_project(db_session, "A")

    chat_history_module.chat_with_ai(project_id=project_a, tab="problems", question="¿Cuál es el problema?", db=db_session)

    assert len(fake_llm_capture) == 1
    call = fake_llm_capture[0]
    assert call["tab"] == "problems"  # canonical section, no "problems_general" ni variantes
    assert "Problema central A" in call["context"]
    assert "Objetivo general A" not in call["context"]
    assert "Alternativa seleccionada A" not in call["context"]
    assert "Cadena A" not in call["context"]


# ---------------------------------------------------------------------------
# 3. objectives contiene problem_tree + planning_alignment
# ---------------------------------------------------------------------------

def test_endpoint_objectives_contains_problem_tree_and_planning_alignment(db_session, fake_llm_capture):
    project_a = _seed_project(db_session, "A")

    chat_history_module.chat_with_ai(project_id=project_a, tab="objectives", question="¿Cuál es el objetivo?", db=db_session)

    context = fake_llm_capture[0]["context"]
    assert "Objetivo general A" in context
    assert "Problema central A" in context  # problem_tree
    assert "PND A" in context  # planning_alignment (national_development_plan)


# ---------------------------------------------------------------------------
# 4. alternatives: current contiene TODAS las alternativas
# ---------------------------------------------------------------------------

def test_endpoint_alternatives_current_contains_all(db_session, fake_llm_capture):
    project_a = _seed_project(db_session, "A")

    chat_history_module.chat_with_ai(project_id=project_a, tab="alternatives_general", question="¿Qué alternativas hay?", db=db_session)

    context = fake_llm_capture[0]["context"]
    assert fake_llm_capture[0]["tab"] == "alternatives"
    assert "Alternativa seleccionada A" in context
    assert "Alternativa inactiva A" in context


# ---------------------------------------------------------------------------
# 5. requirements recibe selected_alternative
# ---------------------------------------------------------------------------

def test_endpoint_requirements_receives_selected_alternative(db_session, fake_llm_capture):
    project_a = _seed_project(db_session, "A")

    chat_history_module.chat_with_ai(project_id=project_a, tab="requirements_general", question="¿Qué se requiere?", db=db_session)

    context = fake_llm_capture[0]["context"]
    assert fake_llm_capture[0]["tab"] == "requirements"
    assert "Bien/Servicio A" in context
    assert "Alternativa seleccionada A" in context


# ---------------------------------------------------------------------------
# 6-7-8. selected_alternative: 0 / 1 / N activas (vía endpoint, sin 500)
# ---------------------------------------------------------------------------

def _seed_minimal_project_with_alternatives(db, active_flags):
    project = Project(name="Proyecto req")
    db.add(project)
    db.flush()
    from app.models.requirements_general import RequirementsGeneral
    from app.models.objectives import Objectives

    db.add(Objectives(project_id=project.id, general_objective="Objetivo req"))
    db.add(RequirementsGeneral(project_id=project.id, requirements_analysis="Analisis"))
    ag = AlternativesGeneral(project_id=project.id, solution_alternatives=True, cost=True, profitability=True)
    db.add(ag)
    db.flush()
    for idx, active in enumerate(active_flags, 1):
        db.add(Alternatives(alternative_id=ag.id, name=f"Alt {idx}", active=active, state="Estado"))
    db.commit()
    return project.id


def test_endpoint_requirements_zero_active_alternatives(db_session, fake_llm_capture):
    project_id = _seed_minimal_project_with_alternatives(db_session, [False, False])
    chat_history_module.chat_with_ai(project_id=project_id, tab="requirements_general", question="q", db=db_session)
    context = fake_llm_capture[0]["context"]
    assert "Alt 1" not in context
    assert "Alt 2" not in context


def test_endpoint_requirements_one_active_alternative(db_session, fake_llm_capture):
    project_id = _seed_minimal_project_with_alternatives(db_session, [False, True])
    chat_history_module.chat_with_ai(project_id=project_id, tab="requirements_general", question="q", db=db_session)
    context = fake_llm_capture[0]["context"]
    assert "Alt 2" in context


def test_endpoint_requirements_multiple_active_alternatives_no_500(db_session, fake_llm_capture):
    project_id = _seed_minimal_project_with_alternatives(db_session, [True, True])
    # No debe lanzar HTTPException/500: se informa la inconsistencia en el contexto.
    chat_history_module.chat_with_ai(project_id=project_id, tab="requirements_general", question="q", db=db_session)
    context = fake_llm_capture[0]["context"]
    assert "Inconsistencia" in context


# ---------------------------------------------------------------------------
# 9. value_chain conserva objective -> product -> activities
# ---------------------------------------------------------------------------

def test_endpoint_value_chain_hierarchy(db_session, fake_llm_capture):
    project_a = _seed_project(db_session, "A")
    chat_history_module.chat_with_ai(project_id=project_a, tab="value_chain", question="¿Cómo es la cadena?", db=db_session)
    context = fake_llm_capture[0]["context"]
    assert "Cadena A" in context
    assert "Objetivo cadena A" in context
    assert "Producto A" in context
    assert "Actividad A" in context


# ---------------------------------------------------------------------------
# 10. proyecto A/B nunca mezcla datos (a nivel de endpoint)
# ---------------------------------------------------------------------------

def test_endpoint_project_isolation(db_session, fake_llm_capture):
    _seed_global_tables(db_session)
    project_a = _seed_project(db_session, "A")
    project_b = _seed_project(db_session, "B")

    chat_history_module.chat_with_ai(project_id=project_a, tab="value_chain", question="q", db=db_session)
    chat_history_module.chat_with_ai(project_id=project_b, tab="value_chain", question="q", db=db_session)

    context_a = fake_llm_capture[0]["context"]
    context_b = fake_llm_capture[1]["context"]
    assert "Cadena A" in context_a and "Cadena B" not in context_a
    assert "Cadena B" in context_b and "Cadena A" not in context_b


# ---------------------------------------------------------------------------
# 11. session A/B nunca mezcla historial
# ---------------------------------------------------------------------------

def test_endpoint_session_history_isolation(db_session, fake_llm_capture):
    project_a = _seed_project(db_session, "A")
    project_b = _seed_project(db_session, "B")

    chat_history_module.chat_with_ai(project_id=project_a, tab="problems", question="Pregunta A1", db=db_session)
    chat_history_module.chat_with_ai(project_id=project_b, tab="problems", question="Pregunta B1", db=db_session)
    chat_history_module.chat_with_ai(project_id=project_a, tab="problems", question="Pregunta A2", db=db_session)

    history_a = chat_history_module.get_chat_history(project_id=project_a, tab="problems", db=db_session)
    history_b = chat_history_module.get_chat_history(project_id=project_b, tab="problems", db=db_session)

    messages_a = {m.message for m in history_a}
    messages_b = {m.message for m in history_b}
    assert "Pregunta A1" in messages_a and "Pregunta A2" in messages_a
    assert "Pregunta B1" not in messages_a
    assert "Pregunta B1" in messages_b
    assert "Pregunta A1" not in messages_b and "Pregunta A2" not in messages_b


# ---------------------------------------------------------------------------
# 12. tab de persistencia vs canonical section para IA
# ---------------------------------------------------------------------------

def test_chat_history_persists_under_original_tab(db_session, fake_llm_capture):
    project_a = _seed_project(db_session, "A")
    chat_history_module.chat_with_ai(project_id=project_a, tab="requirements_general", question="q", db=db_session)

    # El historial se guarda bajo el tab ORIGINAL (persistencia), aunque el
    # LLM reciba la sección canónica ("requirements").
    stored = db_session.query(chat_history_module.ChatHistory).filter(
        chat_history_module.ChatHistory.project_id == project_a
    ).all()
    tabs_used = {m.tab for m in stored}
    assert tabs_used == {"requirements_general"}
    assert fake_llm_capture[0]["tab"] == "requirements"


# ---------------------------------------------------------------------------
# 13. prompt: question aparece una sola vez
# ---------------------------------------------------------------------------

def test_prompt_question_appears_once(db_session):
    project_a = _seed_project(db_session, "A")
    manager = _make_test_llm_manager()
    context_manager = ContextManager()
    semantic_context = context_manager.build_semantic_context(db=db_session, project_id=project_a, section="problems")
    from app.ai.context.context_manager import render_semantic_context
    rendered_context = render_semantic_context(semantic_context)

    question = "¿Cuál es el problema central del proyecto?"
    full_prompt = manager.ask(question=question, tab="problems", context=rendered_context, chat_history=None)

    assert full_prompt.count(question) == 1


# ---------------------------------------------------------------------------
# 14. prompt: project context y RAG en bloques separados
# ---------------------------------------------------------------------------

def test_prompt_project_context_and_rag_are_separate_blocks(db_session):
    project_a = _seed_project(db_session, "A")
    rag_text = "[DOC MGA] La MGA define el árbol de problemas como técnica metodológica."
    manager = _make_test_llm_manager(rag_text=rag_text)
    context_manager = ContextManager()
    semantic_context = context_manager.build_semantic_context(db=db_session, project_id=project_a, section="problems")
    from app.ai.context.context_manager import render_semantic_context
    rendered_context = render_semantic_context(semantic_context)

    full_prompt = manager.ask(question="¿Cuál es el problema?", tab="problems", context=rendered_context, chat_history=None)

    assert "=== INFORMACIÓN REGISTRADA DEL PROYECTO ===" in full_prompt
    assert "=== CONTEXTO METODOLÓGICO MGA (RAG) ===" in full_prompt
    assert rag_text in full_prompt
    # El texto del RAG no debe aparecer duplicado dentro del bloque de proyecto.
    project_block = full_prompt.split("=== CONTEXTO METODOLÓGICO MGA (RAG) ===")[0]
    assert rag_text not in project_block
    assert full_prompt.count(rag_text) == 1
    assert "Problema central A" in full_prompt


# ---------------------------------------------------------------------------
# 14 (LLM/endpoint del fallo): manejo de error existente
# ---------------------------------------------------------------------------

def test_endpoint_llm_failure_returns_500(db_session, monkeypatch):
    from fastapi import HTTPException

    project_a = _seed_project(db_session, "A")

    def _raise_ask(*args, **kwargs):
        raise RuntimeError("Proveedor LLM no disponible")

    monkeypatch.setattr(chat_history_module.llm_manager, "ask", _raise_ask)

    with pytest.raises(HTTPException) as exc_info:
        chat_history_module.chat_with_ai(project_id=project_a, tab="problems", question="q", db=db_session)
    assert exc_info.value.status_code == 500
