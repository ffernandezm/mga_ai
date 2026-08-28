"""Fixtures: siembran en BD los datos de cada caso de evaluación.

Cada fixture recibe una sesión SQLAlchemy aislada y devuelve el `project_id`.
El contexto que verá el LLM se construye después por el flujo de producción
(ContextLoaders -> ContextManager), nunca desde el YAML.

Cada fixture siembra los objetos upstream que la sección requiere según
`module_dependencies`, más un defecto controlado que la respuesta debería
detectar.
"""

from __future__ import annotations

from typing import Callable, Dict

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.database import Base
from app.models import *  # noqa: F401,F403  (registra todos los modelos en Base.metadata)
from app.models.activity import Activity
from app.models.affected_population import AffectedPopulation
from app.models.alternatives import Alternatives
from app.models.alternatives_general import AlternativesGeneral
from app.models.characteristics_population import CharacteristicsPopulation
from app.models.development_plans import DevelopmentPlans
from app.models.direct_causes import DirectCause
from app.models.direct_effects import DirectEffect
from app.models.indirect_causes import IndirectCause
from app.models.indirect_effects import IndirectEffect
from app.models.intervention_population import InterventionPopulation
from app.models.localization import Localization
from app.models.localization_general import LocalizationGeneral
from app.models.objectives import Objectives
from app.models.objectives_causes import ObjectivesCauses
from app.models.objectives_indicators import ObjectivesIndicator
from app.models.participants import Participants
from app.models.participants_general import ParticipantsGeneral
from app.models.pnd import Pnd
from app.models.population import Population
from app.models.problems import Problems
from app.models.product import Product
from app.models.project import Project
from app.models.project_localization import ProjectLocalization
from app.models.requirements import Requirement
from app.models.requirements_general import RequirementsGeneral
from app.models.technical_analysis import TechnicalAnalysis
from app.models.value_chain import ValueChain
from app.models.value_chain_objectives import ValueChainObjectives


def build_case_session() -> Session:
    """Sesión SQLite en memoria exclusiva del caso (garantiza aislamiento)."""
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    return sessionmaker(autocommit=False, autoflush=False, bind=engine)()


# ---------------------------------------------------------------------------
# Bloques reutilizables
# ---------------------------------------------------------------------------

def _project(db: Session) -> Project:
    project = Project(
        name="Mejoramiento de la vía terciaria Tunja - Vereda El Carmen",
        description="Mejoramiento de 10 km de vía terciaria que conecta la zona rural con la cabecera municipal",
        process="Mejoramiento",
        object_desc="Mejorar las condiciones de transitabilidad de la vía terciaria",
        intervention_type="Mejoramiento",
        project_typology="Infraestructura de transporte",
        main_product="Vía terciaria mejorada",
        sector="Transporte",
    )
    db.add(project)
    db.flush()
    db.add(
        ProjectLocalization(
            project_id=project.id,
            region="Región Andina",
            department="Boyacá",
            municipality="Tunja",
        )
    )
    return project


def _planning_alignment(db: Session, project_id: int) -> None:
    plan = DevelopmentPlans(
        project_id=project_id,
        national_development_plan="Plan Nacional de Desarrollo 2022-2026",
        program="Programa de vías para la reactivación rural",
        departmental_or_sectoral_development_plan="Plan de Desarrollo de Boyacá",
        strategy_departmental="Conectividad rural",
    )
    db.add(plan)
    db.flush()
    db.add(
        Pnd(
            development_plan_id=plan.id,
            transformation="Ordenamiento del territorio alrededor del agua",
            pillar="Hábitat y conectividad",
            catalyst="Infraestructura para la equidad",
            component="Vías terciarias",
        )
    )


def _problem_tree(db: Session, project_id: int, extra_direct_causes=()) -> Problems:
    problem = Problems(
        project_id=project_id,
        central_problem="Bajas condiciones de transitabilidad en la vía terciaria que comunica la vereda El Carmen con la cabecera municipal",
        current_description="La vía presenta deterioro de la capa de rodadura y pérdida de obras de drenaje en varios tramos",
        magnitude_problem="Cerca del 60% de los 10 km de la vía presenta deterioro y en temporada de lluvias hay tramos intransitables",
    )
    db.add(problem)
    db.flush()

    causes = ["Deterioro de la capa de rodadura de la vía", *extra_direct_causes]
    for description in causes:
        cause = DirectCause(problem_id=problem.id, description=description)
        db.add(cause)
        db.flush()
        if description == causes[0]:
            db.add(IndirectCause(direct_cause_id=cause.id, description="Ausencia de mantenimiento rutinario periódico"))

    effect = DirectEffect(problem_id=problem.id, description="Incremento de los tiempos de desplazamiento de la población rural")
    db.add(effect)
    db.flush()
    db.add(IndirectEffect(direct_effect_id=effect.id, description="Pérdida de competitividad de la producción agrícola veredal"))
    return problem


def _participants(db: Session, project_id: int, extra=()) -> None:
    general = ParticipantsGeneral(
        project_id=project_id,
        participants_analisis="Identificación de actores vinculados al mejoramiento de la vía terciaria",
    )
    db.add(general)
    db.flush()
    base = [
        dict(
            participant_actor="Alcaldía Municipal de Tunja",
            participant_entity="Municipio",
            interest_expectative="Mejorar la conectividad rural del municipio",
            rol="Ejecutor",
            contribution_conflicts="Aporta recursos de cofinanciación",
        ),
        dict(
            participant_actor="Junta de Acción Comunal vereda El Carmen",
            participant_entity="Organización comunitaria",
            interest_expectative="Reducir tiempos de desplazamiento hacia la cabecera",
            rol="Beneficiario",
            contribution_conflicts="Participa en las jornadas de socialización",
        ),
    ]
    for row in [*base, *extra]:
        db.add(Participants(participants_general_id=general.id, **row))


def _population(db: Session, project_id: int, affected: int, intervention: int) -> None:
    population = Population(
        project_id=project_id,
        population_type_affected="Personas",
        population_number_affected=affected,
        population_info_affected="Habitantes de la vereda El Carmen que usan la vía para acceder a servicios",
        population_type_intervention="Personas",
        population_number_intervention=intervention,
        population_info_intervention="Habitantes que se benefician directamente del mejoramiento de la vía",
    )
    db.add(population)
    db.flush()
    db.add(AffectedPopulation(population_id=population.id, region="Región Andina", department="Boyacá", city="Tunja"))
    db.add(InterventionPopulation(population_id=population.id, region="Región Andina", department="Boyacá", city="Tunja"))
    db.add(
        CharacteristicsPopulation(
            population_id=population.id,
            classification="Zona de residencia",
            detail="Rural",
            people_number=intervention,
            information="Población mayoritariamente dedicada a la actividad agrícola",
        )
    )


def _objectives(db: Session, project_id: int, extra_specifics=()) -> None:
    objectives = Objectives(
        project_id=project_id,
        general_problem="Bajas condiciones de transitabilidad en la vía terciaria",
        general_objective="Mejorar las condiciones de transitabilidad de la vía terciaria que comunica la vereda El Carmen con la cabecera municipal",
    )
    db.add(objectives)
    db.flush()
    base = [
        dict(
            type="Causa directa",
            cause_related="Deterioro de la capa de rodadura de la vía",
            specifics_objectives="Mejorar el estado de la capa de rodadura de la vía",
        )
    ]
    for row in [*base, *extra_specifics]:
        db.add(ObjectivesCauses(objective_id=objectives.id, **row))
    db.add(
        ObjectivesIndicator(
            objective_id=objectives.id,
            indicator="Kilómetros de vía terciaria mejorados",
            unit="Kilómetros",
            meta=10.0,
            source_type="Informe de interventoría",
            source_validation="Acta de recibo final de obra",
        )
    )


def _alternatives(db: Session, project_id: int, rows) -> None:
    general = AlternativesGeneral(project_id=project_id, solution_alternatives=True, cost=True, profitability=True)
    db.add(general)
    db.flush()
    for row in rows:
        db.add(Alternatives(alternative_id=general.id, **row))


def _requirements(db: Session, project_id: int, rows) -> None:
    general = RequirementsGeneral(
        project_id=project_id,
        requirements_analysis="Estudio de necesidades de bienes y servicios para el mejoramiento de la vía",
    )
    db.add(general)
    db.flush()
    for row in rows:
        db.add(Requirement(requirements_general_id=general.id, **row))


_STANDARD_REQUIREMENT = dict(
    good_service_name="Vía terciaria mejorada",
    good_service_description="Mejoramiento de la capa de rodadura y obras de drenaje",
    supply_description="Actualmente la vía se encuentra en afirmado sin obras de drenaje en 6 km",
    demand_description="Tránsito promedio diario de 120 vehículos, incluidos vehículos de carga agrícola",
    unit_of_measure="Kilómetros",
    start_year=2025,
    end_year=2027,
    last_projected_year=2027,
)

_SELECTED_ALTERNATIVE = dict(
    name="Mejoramiento con placa huella en tramos críticos y afirmado en el resto",
    active=True,
    state="Seleccionada",
)


# ---------------------------------------------------------------------------
# Fixtures por caso (cada uno con un defecto controlado)
# ---------------------------------------------------------------------------

def problems_cause_as_missing_solution(db: Session) -> int:
    """Defecto: una causa directa está formulada como ausencia de una solución."""
    project = _project(db)
    _planning_alignment(db, project.id)
    _problem_tree(
        db,
        project.id,
        extra_direct_causes=["Falta de construcción de una variante pavimentada hacia la vereda"],
    )
    db.commit()
    return project.id


def participants_actor_without_coherent_role(db: Session) -> int:
    """Defecto: un participante cuyo rol/interés no se relaciona con el problema vial."""
    project = _project(db)
    _planning_alignment(db, project.id)
    _problem_tree(db, project.id)
    _participants(
        db,
        project.id,
        extra=[
            dict(
                participant_actor="Cooperativa de artesanos del casco urbano",
                participant_entity="Organización privada",
                interest_expectative="Ampliar la comercialización de artesanías en ferias regionales",
                rol="Cooperante",
                contribution_conflicts="Sin aportes definidos para el proyecto",
            )
        ],
    )
    db.commit()
    return project.id


def population_intervention_greater_than_affected(db: Session) -> int:
    """Defecto: la población de intervención supera a la población afectada."""
    project = _project(db)
    _planning_alignment(db, project.id)
    _problem_tree(db, project.id)
    _participants(db, project.id)
    _population(db, project.id, affected=3000, intervention=5000)
    db.commit()
    return project.id


def objectives_specific_without_matching_cause(db: Session) -> int:
    """Defecto: un objetivo específico no corresponde a ninguna causa registrada."""
    project = _project(db)
    _planning_alignment(db, project.id)
    _problem_tree(db, project.id)
    _objectives(
        db,
        project.id,
        extra_specifics=[
            dict(
                type="Causa directa",
                cause_related="Cobertura de conectividad digital en la vereda",
                specifics_objectives="Ampliar la cobertura de internet en la vereda El Carmen",
            )
        ],
    )
    db.commit()
    return project.id


def alternatives_duplicated_course_of_action(db: Session) -> int:
    """Defecto: dos alternativas describen esencialmente el mismo curso de acción."""
    project = _project(db)
    _planning_alignment(db, project.id)
    _problem_tree(db, project.id)
    _participants(db, project.id)
    _population(db, project.id, affected=3000, intervention=2400)
    _objectives(db, project.id)
    _alternatives(
        db,
        project.id,
        rows=[
            dict(
                name="Mejoramiento con placa huella en tramos críticos y afirmado en el resto",
                active=True,
                state="Seleccionada",
            ),
            dict(
                name="Mejoramiento de la vía instalando placa huella en los sectores de mayor pendiente y afirmado en los tramos restantes",
                active=False,
                state="Evaluada",
            ),
            dict(
                name="Construcción de una variante pavimentada por el costado oriental",
                active=False,
                state="Descartada",
            ),
        ],
    )
    db.commit()
    return project.id


def requirements_missing_measurement_and_horizon(db: Session) -> int:
    """Defecto: un bien/servicio sin unidad de medida ni información temporal."""
    project = _project(db)
    _planning_alignment(db, project.id)
    _problem_tree(db, project.id)
    _participants(db, project.id)
    _population(db, project.id, affected=3000, intervention=2400)
    _objectives(db, project.id)
    _alternatives(db, project.id, rows=[_SELECTED_ALTERNATIVE])
    _requirements(
        db,
        project.id,
        rows=[
            _STANDARD_REQUIREMENT,
            dict(
                good_service_name="Obras de drenaje construidas",
                good_service_description="Construcción de alcantarillas y cunetas en los tramos críticos",
                supply_description="Las obras de drenaje existentes se encuentran colmatadas",
                demand_description="Se requieren obras de drenaje en los tramos con mayor afectación por lluvias",
            ),
        ],
    )
    db.commit()
    return project.id


def technical_analysis_introduces_other_alternative(db: Session) -> int:
    """Defecto: el análisis técnico desarrolla una solución distinta de la seleccionada."""
    project = _project(db)
    _planning_alignment(db, project.id)
    _problem_tree(db, project.id)
    _objectives(db, project.id)
    _alternatives(db, project.id, rows=[_SELECTED_ALTERNATIVE])
    _requirements(db, project.id, rows=[_STANDARD_REQUIREMENT])
    db.add(
        TechnicalAnalysis(
            project_id=project.id,
            analysis=(
                "El análisis técnico desarrolla la construcción de una variante pavimentada en concreto "
                "asfáltico por el costado oriental, con un ancho de calzada de 7 metros y obras de arte "
                "nuevas. Se dimensionan las plantas de mezcla y el equipo de pavimentación requerido para "
                "esa variante, así como los volúmenes de excavación del nuevo trazado."
            ),
        )
    )
    db.commit()
    return project.id


def localization_inconsistent_with_target_population(db: Session) -> int:
    """Defecto: la localización registrada no coincide con la ubicación de la población de intervención."""
    project = _project(db)
    _planning_alignment(db, project.id)
    _problem_tree(db, project.id)
    _participants(db, project.id)
    _population(db, project.id, affected=3000, intervention=2400)
    _objectives(db, project.id)
    _alternatives(db, project.id, rows=[_SELECTED_ALTERNATIVE])
    _requirements(db, project.id, rows=[_STANDARD_REQUIREMENT])
    db.add(TechnicalAnalysis(project_id=project.id, analysis="Mejoramiento con placa huella en tramos de mayor pendiente"))

    general = LocalizationGeneral(
        project_id=project.id,
        proximity_to_target_population=True,
        communications=True,
        topography=True,
    )
    db.add(general)
    db.flush()
    db.add(
        Localization(
            localization_general_id=general.id,
            region="Región Caribe",
            department="Atlántico",
            city="Soledad",
            type_group="Corregimiento",
            group="Corregimiento La Playa",
            entity="Alcaldía de Soledad",
            georeferencing=True,
            latitude=10.91,
            longitude=-74.77,
        )
    )
    db.commit()
    return project.id


def value_chain_product_is_actually_activity(db: Session) -> int:
    """Defecto: un 'producto' está formulado como una acción (actividad)."""
    project = _project(db)
    _planning_alignment(db, project.id)
    _problem_tree(db, project.id)
    _objectives(db, project.id)
    _alternatives(db, project.id, rows=[_SELECTED_ALTERNATIVE])
    _requirements(db, project.id, rows=[_STANDARD_REQUIREMENT])
    db.add(TechnicalAnalysis(project_id=project.id, analysis="Mejoramiento con placa huella en tramos de mayor pendiente"))

    chain = ValueChain(project_id=project.id, name="Cadena de valor del mejoramiento vial")
    db.add(chain)
    db.flush()
    objective = ValueChainObjectives(
        project_id=project.id,
        value_chain_id=chain.id,
        name="Mejorar el estado de la capa de rodadura de la vía",
    )
    db.add(objective)
    db.flush()

    correct = Product(
        project_id=project.id,
        value_chain_objective_id=objective.id,
        name="Vía terciaria mejorada",
        description="Kilómetros de vía con placa huella y afirmado en condiciones de transitabilidad",
        measured_through="Kilómetros",
        quantity=10.0,
        cost=4200.0,
        stage="Inversión",
    )
    db.add(correct)
    db.flush()
    db.add(
        Activity(
            project_id=project.id,
            product_id=correct.id,
            description="Conformación de la subrasante y colocación del material de afirmado",
            cost=1800.0,
            stage="Inversión",
        )
    )

    defective = Product(
        project_id=project.id,
        value_chain_objective_id=objective.id,
        name="Realizar la interventoría técnica de las obras",
        description="Seguimiento y control técnico durante la ejecución de las obras del contrato",
        measured_through="Kilómetros",
        quantity=10.0,
        cost=300.0,
        stage="Inversión",
    )
    db.add(defective)
    db.flush()
    db.add(
        Activity(
            project_id=project.id,
            product_id=defective.id,
            description="Elaboración de los informes mensuales de interventoría",
            cost=300.0,
            stage="Inversión",
        )
    )
    db.commit()
    return project.id


FIXTURES: Dict[str, Callable[[Session], int]] = {
    "problems_cause_as_missing_solution": problems_cause_as_missing_solution,
    "participants_actor_without_coherent_role": participants_actor_without_coherent_role,
    "population_intervention_greater_than_affected": population_intervention_greater_than_affected,
    "objectives_specific_without_matching_cause": objectives_specific_without_matching_cause,
    "alternatives_duplicated_course_of_action": alternatives_duplicated_course_of_action,
    "requirements_missing_measurement_and_horizon": requirements_missing_measurement_and_horizon,
    "technical_analysis_introduces_other_alternative": technical_analysis_introduces_other_alternative,
    "localization_inconsistent_with_target_population": localization_inconsistent_with_target_population,
    "value_chain_product_is_actually_activity": value_chain_product_is_actually_activity,
}
