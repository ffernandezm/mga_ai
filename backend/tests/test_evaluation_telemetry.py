from types import SimpleNamespace

from app.models.evaluation_telemetry import (
    EvaluationEventCreate,
    EvaluationSessionCreate,
    EvaluationSessionFinish,
    finish_evaluation_session,
    list_evaluation_sessions,
    record_evaluation_event,
    start_evaluation_session,
)
from app.models.project import Project


def test_evaluation_session_records_query_and_completion(db_session):
    project = Project(name="Evaluación")
    db_session.add(project)
    db_session.commit()
    session = start_evaluation_session(EvaluationSessionCreate(participant_id="P01", project_id=project.id, task="flujo"), db_session)
    record_evaluation_event(session.id, EvaluationEventCreate(section="problems", event_type="llm_query", llm_duration_ms=120, rag_enabled=True), db_session)
    finish_evaluation_session(session.id, EvaluationSessionFinish(completed=True), db_session)
    records = list_evaluation_sessions(db_session)
    assert records[0]["participant_id"] == "P01"
    assert records[0]["llm_queries"] == 1
    assert records[0]["completed"] is True