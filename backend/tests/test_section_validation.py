import pytest
from fastapi import HTTPException

from app.models.chat_history import ensure_chat_prerequisites
from app.models.direct_causes import DirectCause
from app.models.direct_effects import DirectEffect
from app.models.problems import Problems
from app.models.project import Project
from app.models.population import Population
from app.models.development_plans import DevelopmentPlans
from app.models.pnd import Pnd
from app.models.alternatives import Alternatives
from app.models.alternatives_general import AlternativesGeneral
from app.models.participants import Participants
from app.models.participants_general import ParticipantsGeneral
from app.section_validation.schemas import SectionStatus
from app.section_validation.catalog import get_section_field_catalog
from app.section_validation.section_rules import SECTION_ORDER
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
    assert result.required_fields_completed == 5
    assert result.required_fields_total == 5
    assert result.completion_percent == 100


def test_development_plan_requires_program_national_plan_and_pnd_detail(db_session):
    project = _project(db_session)
    db_session.add(DevelopmentPlans(project_id=project.id, program="", national_development_plan=""))
    db_session.commit()

    result = SectionValidationService(db_session).validate_section(project.id, "development_plans", include_prerequisites=False)

    assert {field.key for field in result.missing_fields} == {"program", "national_development_plan", "pnds"}


def test_development_plan_is_complete_with_required_fields_only(db_session):
    project = _project(db_session)
    plan = DevelopmentPlans(project_id=project.id, program="Programa", national_development_plan="Plan Nacional")
    db_session.add(plan)
    db_session.flush()
    db_session.add(Pnd(development_plan_id=plan.id, transformation="Transformación"))
    db_session.commit()

    result = SectionValidationService(db_session).validate_section(project.id, "development_plans", include_prerequisites=False)

    assert result.complete is True
    assert result.required_fields_completed == 3
    assert result.required_fields_total == 3


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


def test_multiple_active_alternatives_do_not_block_identification(db_session):
    project = _project(db_session)
    general = AlternativesGeneral(project_id=project.id, solution_alternatives=True, cost=True, profitability=True)
    general.alternatives = [
        Alternatives(name="Alternativa A", active=True, state="En análisis"),
        Alternatives(name="Alternativa B", active=True, state="En análisis"),
    ]
    db_session.add(general)
    db_session.commit()

    result = SectionValidationService(db_session).validate_section(project.id, "alternatives", include_prerequisites=False)

    assert result.complete is True
    assert result.blocking_rules == []


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


def test_chat_is_available_when_upstream_section_is_incomplete(db_session):
    project = _project(db_session)

    result = ensure_chat_prerequisites(db_session, project.id, "problems")
    assert result.incomplete_prerequisites == ["development_plans"]


def _participant_result(db_session, actor="Actor", entity="Entidad", role="Beneficiario", contribution="Aporte"):
    project = _project(db_session)
    general = ParticipantsGeneral(project_id=project.id, participants_analisis="Análisis")
    general.participants = [Participants(
        participant_actor=actor,
        participant_entity=entity,
        interest_expectative="Interés",
        rol=role,
        contribution_conflicts=contribution,
    )]
    db_session.add(general)
    db_session.commit()
    return SectionValidationService(db_session).validate_section(project.id, "participants", False)


def test_participant_actor_and_entity_are_independent_required_fields(db_session):
    actor_empty = _participant_result(db_session, actor="")
    assert any(field.key.endswith(".actor") for field in actor_empty.missing_fields)

    entity_empty = _participant_result(db_session, entity="")
    assert any(field.key.endswith(".entity") for field in entity_empty.missing_fields)

    complete = _participant_result(db_session)
    assert complete.complete is True


@pytest.mark.parametrize(
    ("role", "expected_message"),
    [
        ("Beneficiario", "Complete la contribución del participante."),
        ("Cooperante", "Complete la contribución del participante."),
        ("Oponente", "Complete la estrategia de gestión del participante."),
        ("Perjudicado", "Complete la estrategia de gestión del participante."),
    ],
)
def test_participant_contribution_field_message_depends_on_role(db_session, role, expected_message):
    result = _participant_result(db_session, role=role, contribution="")
    missing = next(field for field in result.missing_fields if field.key.endswith(".contribution_conflicts"))
    assert missing.label == "Contribución o estrategia de gestión"
    assert missing.message == expected_message


def test_all_required_validator_keys_are_in_section_catalog(db_session):
    def base_key(key):
        parts = key.split(".")
        if len(parts) >= 3 and parts[0] == "participants":
            return {"actor": "participant_actor", "entity": "participant_entity"}.get(parts[2], parts[2])
        if len(parts) >= 3 and parts[0] in {"objectives_indicators", "requirements", "localization", "products", "activities"}:
            return parts[2]
        if len(parts) == 3 and parts[0] == "direct_causes":
            return parts[2]
        if len(parts) == 3 and parts[0] == "direct_effects":
            return parts[2]
        return parts[0]

    catalog_by_section = {
        section: {field["field_key"] for field in get_section_field_catalog(section)}
        for section in SECTION_ORDER
    }
    project = _project(db_session)
    for section in SECTION_ORDER:
        result = SectionValidationService(db_session).validate_section(project.id, section, False)
        unknown = {base_key(field.key) for field in result.missing_fields} - catalog_by_section[section]
        assert unknown == set(), f"{section} reporta claves fuera del catálogo: {unknown}"