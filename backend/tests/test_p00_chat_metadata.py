from types import SimpleNamespace

import app.models.chat_history as chat_history_module
from app.ai.context.context_manager import ContextManager, render_semantic_context
from app.ai.context.select_domains import validate_suggested_value
from app.models.direct_causes import DirectCause
from app.models.direct_effects import DirectEffect
from app.models.participants import Participants
from app.models.participants_general import ParticipantsGeneral
from app.models.problems import Problems
from app.models.project import Project


def _problem_project(db_session):
    project = Project(name="P00")
    db_session.add(project)
    db_session.flush()
    problem = Problems(project_id=project.id, central_problem="Valor A", current_description="Descripción A", magnitude_problem="Magnitud A")
    db_session.add(problem)
    db_session.flush()
    db_session.add_all([DirectCause(problem_id=problem.id, description="Causa A"), DirectEffect(problem_id=problem.id, description="Efecto A")])
    db_session.commit()
    return project, problem


def test_participant_domain_rejects_value_not_available():
    assert validate_suggested_value("participant_actor", "Ministerio de Educación Nacional (MEN)") is False


def test_participants_context_includes_analysis_and_select_domain(db_session):
    project, _ = _problem_project(db_session)
    general = ParticipantsGeneral(project_id=project.id, participants_analisis="Análisis de los participantes")
    general.participants = [Participants(participant_actor="Departamental", participant_entity="Cauca", interest_expectative="Interés", rol="Cooperante", contribution_conflicts="Aporta")]
    db_session.add(general)
    db_session.commit()

    context = ContextManager().build_semantic_context(db_session, project.id, "participants")
    rendered = render_semantic_context(context)
    assert "Análisis de los participantes" in rendered
    assert "Campos de selección permitidos" in rendered
    assert "Ministerio de Educación Nacional (MEN)" not in rendered


def test_semantic_context_reads_latest_saved_value(db_session):
    project, problem = _problem_project(db_session)
    manager = ContextManager()
    first = render_semantic_context(manager.build_semantic_context(db_session, project.id, "problems"))
    problem.central_problem = "Valor B"
    db_session.commit()
    db_session.expire_all()
    second = render_semantic_context(manager.build_semantic_context(db_session, project.id, "problems"))
    assert "Valor A" in first
    assert "Valor B" in second
    assert "Valor A" not in second


def test_improve_scope_uses_all_current_section_fields_not_history(db_session, monkeypatch):
    project, _ = _problem_project(db_session)
    captured = {}

    def ask(**kwargs):
        captured.update(kwargs)
        return "Mejora integral"

    monkeypatch.setattr(chat_history_module.llm_manager, "ask", ask)
    monkeypatch.setattr(chat_history_module.llm_manager, "rag_manager", SimpleNamespace(get_relevant_sources=lambda *args: []))
    response = chat_history_module.chat_with_ai(project.id, "problems", "", action="improve", db=db_session)
    assert response.generation_status == "generated"
    assert "TODA la sección MGA activa" in captured["question"]
    assert "Valor A" in captured["context"]
    assert "Descripción A" in captured["context"]
    assert "Magnitud A" in captured["context"]


def test_structured_change_accepts_only_mapped_simple_field():
    answer = '''Mejora propuesta\n```json
{"suggested_changes":[{"field_key":"general_objective","field_type":"textarea","suggested_value":"Mejorar cobertura"},{"field_key":"participant_actor","field_type":"select","suggested_value":"Ministerio de Educación Nacional (MEN)"}]}
```'''
    changes = chat_history_module._extract_suggested_changes(answer, {"current": {"objectives": {"general_objective": "Ampliar cobertura"}}})
    assert len(changes) == 1
    assert changes[0].field_key == "general_objective"
    assert changes[0].field_type == "textarea"