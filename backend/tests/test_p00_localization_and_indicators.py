from pydantic import ValidationError

from app.models.localization import LocalizationCreate
from app.models.objectives import Objectives
from app.models.objectives_indicators import ObjectivesIndicatorCreate, create_objective_indicators
from app.models.project import Project
from app.models.localization import Localization
from app.models.localization_general import LocalizationGeneral
from app.section_validation.service import SectionValidationService


def test_departmental_localization_does_not_require_municipality():
    data = LocalizationCreate(administrative_level="departmental", department="Cauca", city="", localization_general_id=1)
    assert data.department == "Cauca"


def test_municipal_localization_allows_empty_municipality():
    data = LocalizationCreate(administrative_level="municipal", department="Cauca", city="", localization_general_id=1)
    assert data.department == "Cauca"


def test_localization_accepts_null_municipality():
    data = LocalizationCreate(administrative_level="municipal", department="Cauca", city=None, localization_general_id=1)
    assert data.city is None


def test_empty_municipality_is_not_missing_for_localization(db_session):
    project = Project(name="Proyecto localizacion")
    db_session.add(project)
    db_session.flush()
    general = LocalizationGeneral(project_id=project.id)
    db_session.add(general)
    db_session.flush()
    db_session.add(Localization(localization_general_id=general.id, department="Cauca", city=""))
    db_session.commit()

    validation = SectionValidationService(db_session).validate_section(project.id, "localization", False)

    assert not any("municipio" in item.label.lower() for item in validation.missing_fields)


def test_indicator_accepts_the_frontend_contract(db_session):
    project = Project(name="P00")
    db_session.add(project)
    db_session.flush()
    objective = Objectives(project_id=project.id, general_problem="Problema", general_objective="Objetivo")
    db_session.add(objective)
    db_session.commit()
    result = create_objective_indicators(ObjectivesIndicatorCreate(indicator="Cobertura", unit="Porcentaje", meta=80, source_type="Administrativa", source_validation="Registro validado", objective_id=objective.id), db_session)
    assert result.objective_id == objective.id