from fastapi import HTTPException

from app.models.direct_causes import DirectCause
from app.models.indirect_causes import IndirectCause
from app.models.objective_cause_sync import sync_objective_causes
from app.models.objectives import Objectives, ObjectivesCreate, create_objective
from app.models.objectives_causes import ObjectivesCauses
from app.models.objectives_indicators import (
    ObjectivesIndicatorCreate,
    create_objective_indicators,
    get_objectives_indicators,
)
from app.models.problems import Problems
from app.models.project import Project


def _project_with_problem(db_session, name="P00"):
    project = Project(name=name)
    db_session.add(project)
    db_session.flush()
    problem = Problems(
        project_id=project.id,
        central_problem="Problema X",
        current_description="Situación",
        magnitude_problem="Magnitud",
    )
    db_session.add(problem)
    db_session.flush()
    direct = DirectCause(problem_id=problem.id, description="Causa directa A")
    db_session.add(direct)
    db_session.flush()
    db_session.add_all([
        IndirectCause(direct_cause_id=direct.id, description="Causa indirecta B"),
        IndirectCause(direct_cause_id=direct.id, description="Causa indirecta C"),
    ])
    objective = Objectives(project_id=project.id, general_problem="", general_objective="Objetivo general")
    db_session.add(objective)
    db_session.commit()
    return project, problem, objective


def test_objective_causes_sync_creates_exact_direct_and_indirect_rows(db_session):
    project, _, objective = _project_with_problem(db_session)

    rows = sync_objective_causes(db_session, project.id)
    db_session.commit()

    assert len(rows) == 3
    persisted = db_session.query(ObjectivesCauses).filter_by(objective_id=objective.id).all()
    assert {(row.type, row.cause_related) for row in persisted} == {
        ("directa", "Causa directa A"),
        ("indirecta", "Causa indirecta B"),
        ("indirecta", "Causa indirecta C"),
    }
    assert all(row.specifics_objectives is None for row in persisted)


def test_objective_creation_after_problem_causes_syncs_relations(db_session):
    project = Project(name="Objetivo posterior")
    db_session.add(project)
    db_session.flush()
    problem = Problems(
        project_id=project.id,
        central_problem="Problema X",
        current_description="Situación",
        magnitude_problem="Magnitud",
    )
    db_session.add(problem)
    db_session.flush()
    db_session.add(DirectCause(problem_id=problem.id, description="Causa existente"))
    db_session.commit()

    objective = create_objective(
        project.id,
        ObjectivesCreate(general_objective="Objetivo general"),
        db_session,
    )

    assert objective.general_problem == "Problema X"
    assert [row.cause_related for row in objective.objectives_causes] == ["Causa existente"]


def test_objectives_context_uses_updated_problem_central(db_session):
    project, problem, _ = _project_with_problem(db_session)
    from app.ai.context.context_manager import ContextManager

    problem.central_problem = "Problema Y"
    db_session.commit()
    context = ContextManager().build_semantic_context(db_session, project.id, "objectives")

    assert context["required"]["problem_tree"]["central_problem"] == "Problema Y"


def test_objective_causes_sync_is_idempotent_and_preserves_specific_objective(db_session):
    project, _, objective = _project_with_problem(db_session)
    sync_objective_causes(db_session, project.id)
    db_session.commit()
    direct_row = db_session.query(ObjectivesCauses).filter_by(objective_id=objective.id, type="directa").one()
    direct_row.specifics_objectives = "Objetivo específico A"
    db_session.commit()

    for _ in range(5):
        sync_objective_causes(db_session, project.id)
        db_session.commit()

    rows = db_session.query(ObjectivesCauses).filter_by(objective_id=objective.id).all()
    assert len(rows) == 3
    assert db_session.query(ObjectivesCauses).filter_by(id=direct_row.id).one().specifics_objectives == "Objetivo específico A"


def test_objective_causes_sync_updates_text_and_removes_deleted_cause(db_session):
    project, problem, objective = _project_with_problem(db_session)
    sync_objective_causes(db_session, project.id)
    db_session.commit()
    direct = problem.direct_causes[0]
    indirect = direct.indirect_causes[0]
    direct.description = "Causa directa actualizada"
    objective_row = db_session.query(ObjectivesCauses).filter_by(
        objective_id=objective.id, cause_id=direct.id, type="directa"
    ).one()
    objective_row.specifics_objectives = "Objetivo conservado"
    db_session.delete(indirect)
    db_session.commit()

    sync_objective_causes(db_session, project.id)
    db_session.commit()

    rows = db_session.query(ObjectivesCauses).filter_by(objective_id=objective.id).all()
    assert len(rows) == 2
    updated = db_session.query(ObjectivesCauses).filter_by(objective_id=objective.id, cause_id=direct.id).one()
    assert updated.cause_related == "Causa directa actualizada"
    assert updated.specifics_objectives == "Objetivo conservado"
    assert all(not (row.type == "indirecta" and row.cause_id == indirect.id) for row in rows)


def test_objective_causes_sync_isolated_by_project(db_session):
    project_a, _, objective_a = _project_with_problem(db_session, "A")
    project_b, _, objective_b = _project_with_problem(db_session, "B")
    sync_objective_causes(db_session, project_a.id)
    sync_objective_causes(db_session, project_b.id)
    db_session.commit()

    rows_a = db_session.query(ObjectivesCauses).filter_by(objective_id=objective_a.id).all()
    rows_b = db_session.query(ObjectivesCauses).filter_by(objective_id=objective_b.id).all()
    assert {row.cause_related for row in rows_a} == {"Causa directa A", "Causa indirecta B", "Causa indirecta C"}
    assert {row.cause_related for row in rows_b} == {"Causa directa A", "Causa indirecta B", "Causa indirecta C"}
    assert {(row.type, row.cause_id) for row in rows_a}.isdisjoint(
        {(row.type, row.cause_id) for row in rows_b}
    )


def test_indicator_create_and_get_contract(db_session):
    project, _, objective = _project_with_problem(db_session)
    payload = ObjectivesIndicatorCreate(
        indicator="Adultos mayores atendidos mediante servicios integrales",
        unit="Número de adultos mayores",
        meta=85,
        source_type="Administrativa",
        source_validation="Registro validado",
        objective_id=objective.id,
    )
    created = create_objective_indicators(payload, db_session)
    assert created.objective_id == objective.id
    listed = get_objectives_indicators(db_session)
    assert any(item.id == created.id and item.meta == 85 for item in listed)


def test_indicator_invalid_objective_is_controlled(db_session):
    payload = ObjectivesIndicatorCreate(
        indicator="Indicador válido",
        unit="Número",
        meta=1,
        source_type="Administrativa",
        source_validation="Registro",
        objective_id=99999,
    )
    try:
        create_objective_indicators(payload, db_session)
    except HTTPException as exc:
        assert exc.status_code == 422
        assert "objective_id" in str(exc.detail)
    else:
        raise AssertionError("Debe rechazar un objective_id inexistente")
