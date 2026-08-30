import pytest
from fastapi import HTTPException

from app.models.chat_history import ensure_chat_prerequisites
from app.models.direct_causes import DirectCause
from app.models.direct_effects import DirectEffect
from app.models.problems import Problems
from app.models.project import Project
from app.models.population import Population
from app.section_validation.schemas import SectionStatus
from app.section_validation.service import SectionValidationService


def _project(db_session):
    project = Project(name="Proyecto de prueba")
    db_session.add(project)
    db_session.commit()
    return project


def test_empty_problem_section_lists_all_required_fields(db_session):
    project = _project(db_session)

    result = SectionValidationService(db_session).validate_section(
        project.id, "problems", include_prerequisites=False
    )

    assert result.complete is False
    assert result.status == SectionStatus.NOT_STARTED
    assert {field.key for field in result.missing_fields} == {
        "central_problem",
        "current_description",
        "magnitude_problem",
        "direct_causes",
        "direct_effects",
    }


def test_partial_problem_section_reports_empty_child(db_session):
    project = _project(db_session)
    problem = Problems(
        project_id=project.id,
        central_problem="Baja cobertura",
        current_description="La cobertura es insuficiente.",
        magnitude_problem="Cobertura actual del 40 %",
    )
    db_session.add(problem)
    db_session.flush()
    db_session.add_all(
        [
            DirectCause(problem_id=problem.id, description=" "),
            DirectEffect(problem_id=problem.id, description="Menor acceso"),
        ]
    )
    db_session.commit()

    result = SectionValidationService(db_session).validate_section(
        project.id, "problem", include_prerequisites=False
    )

    assert result.complete is False
    assert [field.label for field in result.missing_fields] == [
        "Descripción de la causa directa"
    ]


def test_complete_problem_section(db_session):
    project = _project(db_session)
    problem = Problems(
        project_id=project.id,
        central_problem="Baja cobertura",
        current_description="La cobertura es insuficiente.",
        magnitude_problem="Cobertura actual del 40 %",
    )
    db_session.add(problem)
    db_session.flush()
    db_session.add_all(
        [
            DirectCause(problem_id=problem.id, description="Infraestructura insuficiente"),
            DirectEffect(problem_id=problem.id, description="Menor acceso"),
        ]
    )
    db_session.commit()

    result = SectionValidationService(db_session).validate_section(
        project.id, "problems", include_prerequisites=False
    )

    assert result.complete is True
    assert result.status == SectionStatus.COMPLETE
    assert result.missing_fields == []


def test_complete_problem_is_blocked_by_incomplete_development_plan(db_session):
    project = _project(db_session)
    problem = Problems(
        project_id=project.id,
        central_problem="Baja cobertura",
        current_description="La cobertura es insuficiente.",
        magnitude_problem="Cobertura actual del 40 %",
    )
    db_session.add(problem)
    db_session.flush()
    db_session.add_all(
        [
            DirectCause(problem_id=problem.id, description="Infraestructura insuficiente"),
            DirectEffect(problem_id=problem.id, description="Menor acceso"),
        ]
    )
    db_session.commit()

    result = SectionValidationService(db_session).validate_section(project.id, "problems")

    assert result.complete is True
    assert result.status == SectionStatus.BLOCKED
    assert result.prerequisites_complete is False
    assert result.incomplete_prerequisites == ["development_plans"]


def test_population_rejects_negative_and_target_above_affected(db_session):
    project = _project(db_session)
    db_session.add(
        Population(
            project_id=project.id,
            population_number_affected=-1,
            population_info_affected="Censo",
            population_number_intervention=10,
            population_info_intervention="Registro y focalización",
        )
    )
    db_session.commit()

    result = SectionValidationService(db_session).validate_section(
        project.id, "population", include_prerequisites=False
    )

    assert result.complete is False
    assert {rule.key for rule in result.blocking_rules} == {
        "population.non_negative",
        "population.target_lte_affected",
    }


def test_validate_all_returns_sections_in_canonical_order(db_session):
    project = _project(db_session)

    results = SectionValidationService(db_session).validate_all(project.id)

    assert [result.section for result in results] == [
        "development_plans", "problems", "participants", "population",
        "objectives", "alternatives", "requirements", "technical_analysis",
        "localization", "value_chain",
    ]


def test_chat_is_available_in_incomplete_current_section(db_session):
    project = _project(db_session)

    ensure_chat_prerequisites(db_session, project.id, "development_plans")


def test_chat_is_blocked_when_upstream_section_is_incomplete(db_session):
    project = _project(db_session)

    with pytest.raises(HTTPException) as exc_info:
        ensure_chat_prerequisites(db_session, project.id, "problems")

    assert exc_info.value.status_code == 409
    assert exc_info.value.detail["incomplete_prerequisites"] == ["development_plans"]