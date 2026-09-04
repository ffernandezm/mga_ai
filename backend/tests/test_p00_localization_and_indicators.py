from pydantic import ValidationError

from app.models.localization import LocalizationCreate
from app.models.objectives import Objectives
from app.models.objectives_indicators import ObjectivesIndicatorCreate, create_objective_indicators
from app.models.project import Project


def test_departmental_localization_does_not_require_municipality():
    data = LocalizationCreate(administrative_level="departmental", department="Cauca", city="", localization_general_id=1)
    assert data.department == "Cauca"


def test_municipal_localization_requires_municipality():
    try:
        LocalizationCreate(administrative_level="municipal", department="Cauca", city="", localization_general_id=1)
    except ValidationError as exc:
        assert "municipio" in str(exc).lower()
    else:
        raise AssertionError("El nivel municipal debe exigir municipio")


def test_indicator_accepts_the_frontend_contract(db_session):
    project = Project(name="P00")
    db_session.add(project)
    db_session.flush()
    objective = Objectives(project_id=project.id, general_problem="Problema", general_objective="Objetivo")
    db_session.add(objective)
    db_session.commit()
    result = create_objective_indicators(ObjectivesIndicatorCreate(indicator="Cobertura", unit="Porcentaje", meta=80, source_type="Administrativa", source_validation="Registro validado", objective_id=objective.id), db_session)
    assert result.objective_id == objective.id