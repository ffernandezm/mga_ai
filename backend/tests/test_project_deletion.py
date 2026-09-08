from fastapi import HTTPException
from sqlalchemy import text

from app.models.chat_history import ChatHistory
from app.models.evaluation_telemetry import EvaluationEvent, EvaluationSession
from app.models.project import Project, ProjectCreate, create_project, delete_project


def _enable_foreign_keys(db_session):
    db_session.execute(text("PRAGMA foreign_keys=ON"))


def test_delete_project_removes_operational_chat_history(db_session):
    _enable_foreign_keys(db_session)
    project = create_project(ProjectCreate(name="Proyecto DELETE"), db_session)
    project_id = project.id
    db_session.add(ChatHistory(
        project_id=project_id,
        tab="problems",
        session_id="session-delete",
        sender="user",
        message="mensaje",
    ))
    db_session.commit()

    delete_project(project_id, db_session)

    assert db_session.query(Project).filter_by(id=project_id).first() is None
    assert db_session.query(ChatHistory).filter_by(project_id=project_id).count() == 0


def test_delete_project_preserves_evaluation_evidence_and_nulls_project(db_session):
    _enable_foreign_keys(db_session)
    project = create_project(ProjectCreate(name="Proyecto evaluado"), db_session)
    evaluation = EvaluationSession(
        participant_id="P01",
        project_id=project.id,
        configuration={},
    )
    db_session.add(evaluation)
    db_session.flush()
    event = EvaluationEvent(
        evaluation_session_id=evaluation.id,
        event_type="field_saved",
        section="problems",
        payload={},
    )
    db_session.add(event)
    db_session.commit()

    delete_project(project.id, db_session)

    persisted_session = db_session.query(EvaluationSession).filter_by(id=evaluation.id).one()
    assert db_session.query(Project).filter_by(id=project.id).first() is None
    assert persisted_session.project_id is None
    assert db_session.query(EvaluationEvent).filter_by(id=event.id).first() is not None


def test_delete_project_missing_id_is_controlled(db_session):
    try:
        delete_project(999999, db_session)
    except HTTPException as exc:
        assert exc.status_code == 404
    else:
        raise AssertionError("Expected missing project deletion to return 404")