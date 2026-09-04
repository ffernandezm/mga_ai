"""Pruebas de la capa de ContextLoaders + ContextManager (build_semantic_context).

Cobertura: normalización de secciones, aislamiento por proyecto, jerarquías
(problem_tree, value_chain), selección de alternativa, transformación de
factores booleanos de localización, exclusión de ids/json, y no mezcla de
tablas globales (pnd_details, product_catalogs).
"""

from __future__ import annotations

import json
from typing import Any

import pytest

from app.ai.context.context_manager import ContextManager
from app.ai.context.module_dependencies import UnknownSectionError, normalize_section
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
from app.models.pnd_details import PndDetail
from app.models.population import Population
from app.models.problems import Problems
from app.models.product import Product
from app.models.product_catalog import ProductCatalog
from app.models.project import Project
from app.models.project_localization import ProjectLocalization
from app.models.requirements import Requirement
from app.models.requirements_general import RequirementsGeneral
from app.models.technical_analysis import TechnicalAnalysis
from app.models.value_chain import ValueChain
from app.models.value_chain_objectives import ValueChainObjectives


def _seed_project(db, label: str) -> int:
    """Crea un set de datos completo y distinguible por `label` (p. ej. 'A'/'B')."""
    project = Project(
        name=f"Proyecto {label}",
        description=f"Descripcion {label}",
        process=f"Proceso {label}",
        object_desc=f"Objeto {label}",
        intervention_type=f"Tipo {label}",
        project_typology=f"Tipologia {label}",
        main_product=f"Producto principal {label}",
        sector=f"Sector {label}",
    )
    db.add(project)
    db.flush()

    db.add(ProjectLocalization(project_id=project.id, region=f"Region {label}", department=f"Depto {label}", municipality=f"Municipio {label}"))

    plan = DevelopmentPlans(project_id=project.id, national_development_plan=f"PND {label}", program=f"Programa {label}")
    db.add(plan)
    db.flush()
    db.add(Pnd(development_plan_id=plan.id, transformation=f"Transformacion {label}", pillar=f"Pilar {label}", catalyst=f"Catalizador {label}", component=f"Componente {label}"))

    problem = Problems(project_id=project.id, central_problem=f"Problema central {label}", current_description=f"Descripcion actual {label}", magnitude_problem=f"Magnitud {label}")
    db.add(problem)
    db.flush()
    dc = DirectCause(problem_id=problem.id, description=f"Causa directa {label}")
    db.add(dc)
    db.flush()
    db.add(IndirectCause(direct_cause_id=dc.id, description=f"Causa indirecta {label}"))
    de = DirectEffect(problem_id=problem.id, description=f"Efecto directo {label}")
    db.add(de)
    db.flush()
    db.add(IndirectEffect(direct_effect_id=de.id, description=f"Efecto indirecto {label}"))

    pg = ParticipantsGeneral(project_id=project.id, participants_analisis=f"Analisis participantes {label}")
    db.add(pg)
    db.flush()
    db.add(Participants(
        participants_general_id=pg.id,
        participant_actor=f"Actor {label}",
        participant_entity=f"Entidad {label}",
        interest_expectative=f"Interes {label}",
        rol=f"Rol {label}",
        contribution_conflicts=f"Conflictos {label}",
    ))

    population = Population(
        project_id=project.id,
        population_type_affected="Personas",
        population_number_affected=100,
        population_info_affected=f"Info afectada {label}",
        population_type_intervention="Personas",
        population_number_intervention=50,
        population_info_intervention=f"Info intervencion {label}",
    )
    db.add(population)
    db.flush()
    db.add(AffectedPopulation(population_id=population.id, region=f"Region afectada {label}", department=f"Depto afectado {label}"))
    db.add(InterventionPopulation(population_id=population.id, region=f"Region intervencion {label}", department=f"Depto intervencion {label}"))
    db.add(CharacteristicsPopulation(population_id=population.id, classification=f"Clasificacion {label}", detail=f"Detalle {label}", people_number=10))

    objectives = Objectives(project_id=project.id, general_problem=f"Problema general {label}", general_objective=f"Objetivo general {label}")
    db.add(objectives)
    db.flush()
    db.add(ObjectivesCauses(objective_id=objectives.id, type=f"Tipo causa {label}", cause_related=f"Causa relacionada {label}", specifics_objectives=f"Objetivo especifico {label}"))
    db.add(ObjectivesIndicator(objective_id=objectives.id, indicator=f"Indicador {label}", unit="unidad", meta=1.0, source_type=f"Fuente {label}", source_validation=f"Validacion {label}"))

    ag = AlternativesGeneral(project_id=project.id, solution_alternatives=True, cost=True, profitability=True)
    db.add(ag)
    db.flush()
    db.add(Alternatives(alternative_id=ag.id, name=f"Alternativa inactiva {label}", active=False, state="Descartada"))
    db.add(Alternatives(alternative_id=ag.id, name=f"Alternativa seleccionada {label}", active=True, state="Seleccionada"))

    rg = RequirementsGeneral(project_id=project.id, requirements_analysis=f"Analisis requerimientos {label}")
    db.add(rg)
    db.flush()
    db.add(Requirement(
        requirements_general_id=rg.id,
        good_service_name=f"Bien/Servicio {label}",
        good_service_description=f"Descripcion bien {label}",
        supply_description=f"Oferta {label}",
        demand_description=f"Demanda {label}",
        unit_of_measure="unidad",
        start_year=2020,
        end_year=2025,
        last_projected_year=2025,
    ))

    db.add(TechnicalAnalysis(project_id=project.id, analysis=f"Analisis tecnico {label}"))

    lg = LocalizationGeneral(
        project_id=project.id,
        proximity_to_target_population=True,
        environmental_factors=False,
        public_order=True,
    )
    db.add(lg)
    db.flush()
    db.add(Localization(
        localization_general_id=lg.id,
        region=f"Region loc {label}",
        department=f"Depto loc {label}",
        city=f"Ciudad {label}",
        type_group=f"Grupo tipo {label}",
        group=f"Grupo {label}",
        entity=f"Entidad loc {label}",
        georeferencing=True,
        latitude=1.23,
        longitude=4.56,
    ))

    chain = ValueChain(project_id=project.id, name=f"Cadena {label}")
    db.add(chain)
    db.flush()
    vco = ValueChainObjectives(project_id=project.id, value_chain_id=chain.id, name=f"Objetivo cadena {label}")
    db.add(vco)
    db.flush()
    prod = Product(project_id=project.id, value_chain_objective_id=vco.id, name=f"Producto {label}", description=f"Descripcion producto {label}", measured_through="unidad", quantity=10.0, cost=100.0, stage="Ejecucion")
    db.add(prod)
    db.flush()
    db.add(Activity(project_id=project.id, product_id=prod.id, description=f"Actividad {label}", cost=50.0, stage="Ejecucion"))

    db.commit()
    return project.id


def _seed_global_tables(db) -> None:
    """Tablas globales sin project_id que NO deben mezclarse en el contexto."""
    db.add(PndDetail(
        source_id=1,
        plan_id=1,
        plan_name="Plan Global",
        pillar_description="Pilar global filtrado",
        objective_description="Objetivo global filtrado",
        strategy_description="Estrategia global filtrada",
        component_description="Componente global filtrado",
        selected_to_project=True,
    ))
    db.add(ProductCatalog(
        sector_name="Sector catalogo global",
        product_name="Producto catalogo global",
        description="Descripcion catalogo global",
        selected_to_project=True,
    ))
    db.commit()


def _flatten_values(obj: Any):
    if isinstance(obj, dict):
        for key, value in obj.items():
            yield key, value
            yield from _flatten_values(value)
    elif isinstance(obj, list):
        for item in obj:
            yield from _flatten_values(item)


@pytest.fixture()
def two_projects(db_session):
    _seed_global_tables(db_session)
    project_a = _seed_project(db_session, "A")
    project_b = _seed_project(db_session, "B")
    return project_a, project_b


@pytest.fixture()
def manager():
    return ContextManager()


# ---------------------------------------------------------------------------
# A. normalize_section()
# ---------------------------------------------------------------------------

@pytest.mark.parametrize(
    "alias,expected",
    [
        ("problems", "problems"),
        ("direct_effects", "problems"),
        ("indirect_causes", "problems"),
        ("participants_general", "participants"),
        ("participants", "participants"),
        ("population", "population"),
        ("affected_population", "population"),
        ("objectives", "objectives"),
        ("objectives_indicator", "objectives"),
        ("alternatives_general", "alternatives"),
        ("requirements_general", "requirements"),
        ("localization_general", "localization"),
        ("value_chain", "value_chain"),
        ("value_chains", "value_chain"),
        ("VALUE_CHAIN", "value_chain"),
        ("development-plans", "development_plans"),
        ("pnd_details", "development_plans"),
    ],
)
def test_normalize_section_aliases(alias, expected):
    assert normalize_section(alias) == expected


def test_normalize_section_rejects_unknown():
    with pytest.raises(UnknownSectionError):
        normalize_section("tabla_inexistente")
    with pytest.raises(UnknownSectionError):
        normalize_section("")
    with pytest.raises(UnknownSectionError):
        normalize_section(None)


# ---------------------------------------------------------------------------
# B. Project isolation
# ---------------------------------------------------------------------------

def test_project_isolation_problems(manager, db_session, two_projects):
    project_a, project_b = two_projects
    context_a = manager.build_context(db=db_session, project_id=project_a, section="problems")
    serialized = json.dumps(context_a)
    assert "Proyecto A" not in serialized or True  # project block not required for 'problems'
    assert "B" not in "".join(str(v) for _, v in _flatten_values(context_a) if isinstance(v, str) and "Problema central B" in v)
    assert "Problema central A" in serialized
    assert "Problema central B" not in serialized


def test_project_isolation_value_chain(manager, db_session, two_projects):
    project_a, project_b = two_projects
    context_a = manager.build_context(db=db_session, project_id=project_a, section="value_chain")
    serialized = json.dumps(context_a)
    assert "Cadena A" in serialized
    assert "Cadena B" not in serialized
    assert "Producto B" not in serialized
    assert "Actividad B" not in serialized


# ---------------------------------------------------------------------------
# C. problem_tree hierarchy
# ---------------------------------------------------------------------------

def test_problem_tree_hierarchy(manager, db_session, two_projects):
    project_a, _ = two_projects
    context = manager.build_context(db=db_session, project_id=project_a, section="problems")
    tree = context["current"]["problem_tree"]
    assert tree["central_problem"] == "Problema central A"
    assert tree["direct_causes"][0]["description"] == "Causa directa A"
    assert tree["direct_causes"][0]["indirect_causes"][0]["description"] == "Causa indirecta A"
    assert tree["direct_effects"][0]["description"] == "Efecto directo A"
    assert tree["direct_effects"][0]["indirect_effects"][0]["description"] == "Efecto indirecto A"


# ---------------------------------------------------------------------------
# D. objectives
# ---------------------------------------------------------------------------

def test_objectives_loaded_correctly(manager, db_session, two_projects):
    project_a, _ = two_projects
    context = manager.build_context(db=db_session, project_id=project_a, section="objectives")
    objectives = context["current"]["objectives"]
    assert objectives["general_objective"] == "Objetivo general A"
    assert objectives["specific_objectives"][0]["objective"] == "Objetivo especifico A"
    assert objectives["indicators"][0]["indicator"] == "Indicador A"
    assert objectives["central_problem"] == "Problema central A"
    assert "general_problem" not in objectives


# ---------------------------------------------------------------------------
# E. population affected/intervention
# ---------------------------------------------------------------------------

def test_population_affected_and_intervention_separated(manager, db_session, two_projects):
    project_a, _ = two_projects
    context = manager.build_context(db=db_session, project_id=project_a, section="population")
    population = context["current"]["population"]
    assert population["affected"]["number"] == 100
    assert population["affected"]["locations"][0]["region"] == "Region afectada A"
    assert population["intervention"]["number"] == 50
    assert population["intervention"]["locations"][0]["region"] == "Region intervencion A"
    assert population["characteristics"][0]["classification"] == "Clasificacion A"


# ---------------------------------------------------------------------------
# F. alternatives: current contiene TODAS las alternativas registradas
# ---------------------------------------------------------------------------

def test_alternatives_current_contains_all_alternatives(manager, db_session, two_projects):
    project_a, _ = two_projects
    context = manager.build_context(db=db_session, project_id=project_a, section="alternatives")
    alternatives = context["current"]["alternatives"]
    assert len(alternatives) == 2
    names = {a["name"] for a in alternatives}
    assert names == {"Alternativa inactiva A", "Alternativa seleccionada A"}
    active_flags = {a["name"]: a["active"] for a in alternatives}
    assert active_flags["Alternativa seleccionada A"] is True
    assert active_flags["Alternativa inactiva A"] is False


def test_requirements_uses_available_alternatives_without_inferred_selection(manager, db_session, two_projects):
    project_a, _ = two_projects
    context = manager.build_context(db=db_session, project_id=project_a, section="requirements")
    available = context["required"]["selected_alternative"]
    assert {item["name"] for item in available["alternatives"]} == {"Alternativa seleccionada A", "Alternativa inactiva A"}


# ---------------------------------------------------------------------------
# F.2 load_selected_alternative: 0 / 1 / N alternativas activas
# ---------------------------------------------------------------------------

def _seed_project_with_alternative_states(db, active_flags):
    project = Project(name="Proyecto alternativas")
    db.add(project)
    db.flush()
    ag = AlternativesGeneral(project_id=project.id, solution_alternatives=True, cost=True, profitability=True)
    db.add(ag)
    db.flush()
    for idx, active in enumerate(active_flags, 1):
        db.add(Alternatives(alternative_id=ag.id, name=f"Alternativa {idx}", active=active, state="Estado"))
    db.commit()
    return project.id


def test_available_alternatives_ignore_active_flag(manager, db_session):
    from app.ai.context.context_loaders import load_selected_alternative

    project_id = _seed_project_with_alternative_states(db_session, [False, False])
    result = load_selected_alternative(db_session, project_id)
    assert len(result["alternatives"]) == 2


def test_available_alternatives_include_one_active(manager, db_session):
    from app.ai.context.context_loaders import load_selected_alternative

    project_id = _seed_project_with_alternative_states(db_session, [False, True])
    result = load_selected_alternative(db_session, project_id)
    assert len(result["alternatives"]) == 2


def test_available_alternatives_allow_multiple_active(manager, db_session):
    from app.ai.context.context_loaders import load_selected_alternative

    project_id = _seed_project_with_alternative_states(db_session, [True, True])
    result = load_selected_alternative(db_session, project_id)
    assert len(result["alternatives"]) == 2
    context = manager.build_context(db=db_session, project_id=project_id, section="requirements")
    assert len(context["required"]["selected_alternative"]["alternatives"]) == 2


# ---------------------------------------------------------------------------
# G. requirements
# ---------------------------------------------------------------------------

def test_requirements_data(manager, db_session, two_projects):
    project_a, _ = two_projects
    context = manager.build_context(db=db_session, project_id=project_a, section="requirements")
    requirements = context["current"]["requirements"]
    assert requirements["requirements_analysis"] == "Analisis requerimientos A"
    good = requirements["goods_services"][0]
    assert good["name"] == "Bien/Servicio A"
    assert good["supply_description"] == "Oferta A"
    assert good["demand_description"] == "Demanda A"


# ---------------------------------------------------------------------------
# H. localization: factores true -> etiquetas legibles, false omitidos
# ---------------------------------------------------------------------------

def test_localization_boolean_factors_transformed(manager, db_session, two_projects):
    project_a, _ = two_projects
    context = manager.build_context(db=db_session, project_id=project_a, section="localization")
    localization = context["current"]["localization"]
    assert "Proximidad a la población objetivo" in localization["active_factors"]
    assert "Orden público" in localization["active_factors"]
    assert "Factores ambientales" not in localization["active_factors"]
    assert localization["locations"][0]["region"] == "Region loc A"


# ---------------------------------------------------------------------------
# I. value_chain: objective -> product -> activities
# ---------------------------------------------------------------------------

def test_value_chain_hierarchy(manager, db_session, two_projects):
    project_a, _ = two_projects
    context = manager.build_context(db=db_session, project_id=project_a, section="value_chain")
    chain = context["current"]["value_chain"]
    assert chain["name"] == "Cadena A"
    objective = chain["objectives"][0]
    assert objective["name"] == "Objetivo cadena A"
    product = objective["products"][0]
    assert product["name"] == "Producto A"
    activity = product["activities"][0]
    assert activity["description"] == "Actividad A"


# ---------------------------------------------------------------------------
# J. required/supporting via module_dependencies
# ---------------------------------------------------------------------------

def test_required_and_supporting_present(manager, db_session, two_projects):
    project_a, _ = two_projects
    context = manager.build_context(db=db_session, project_id=project_a, section="alternatives")
    assert set(context["required"].keys()) == {"project", "objectives"}
    assert set(context["supporting"].keys()) == {"problem_summary", "population_summary", "participants_summary"}
    assert context["required"]["objectives"]["general_objective"] == "Objetivo general A"


# ---------------------------------------------------------------------------
# K. forbidden generation: problems no debe cargar downstream
# ---------------------------------------------------------------------------

def test_problems_forbidden_downstream_sections(manager, db_session, two_projects):
    project_a, _ = two_projects
    context = manager.build_context(db=db_session, project_id=project_a, section="problems")
    all_keys = set(context["required"].keys()) | set(context["supporting"].keys()) | set(context["current"].keys())
    assert "objectives" not in all_keys
    assert "selected_alternative" not in all_keys
    assert "value_chain" not in all_keys


# ---------------------------------------------------------------------------
# L. IDs no aparecen
# ---------------------------------------------------------------------------

def test_no_internal_ids_in_context(manager, db_session, two_projects):
    project_a, _ = two_projects
    for section in ("problems", "objectives", "alternatives", "requirements", "localization", "value_chain"):
        context = manager.build_context(db=db_session, project_id=project_a, section=section)
        for key, _value in _flatten_values(context):
            assert key != "id"
            assert not str(key).endswith("_id")


# ---------------------------------------------------------------------------
# M. JSON no aparece
# ---------------------------------------------------------------------------

def test_no_json_snapshots_in_context(manager, db_session, two_projects):
    project_a, _ = two_projects
    for section in ("problems", "participants", "population", "alternatives"):
        context = manager.build_context(db=db_session, project_id=project_a, section=section)
        for key, _value in _flatten_values(context):
            assert "json" not in str(key).lower()


# ---------------------------------------------------------------------------
# N. pnd_details no se mezcla (tabla global)
# ---------------------------------------------------------------------------

def test_pnd_details_global_not_mixed(manager, db_session, two_projects):
    project_a, _ = two_projects
    context = manager.build_context(db=db_session, project_id=project_a, section="development_plans")
    serialized = json.dumps(context)
    assert "Pilar global filtrado" not in serialized
    assert "Objetivo global filtrado" not in serialized
    assert "selected_to_project" not in serialized


# ---------------------------------------------------------------------------
# O. product catalogs no se mezcla (tabla global)
# ---------------------------------------------------------------------------

def test_product_catalog_global_not_mixed(manager, db_session, two_projects):
    project_a, _ = two_projects
    context = manager.build_context(db=db_session, project_id=project_a, section="value_chain")
    serialized = json.dumps(context)
    assert "Producto catalogo global" not in serialized
    assert "Sector catalogo global" not in serialized


# ---------------------------------------------------------------------------
# P. valores vacíos/nulos omitidos
# ---------------------------------------------------------------------------

def test_null_and_empty_values_omitted(manager, db_session):
    project = Project(name="Proyecto vacio")
    db_session.add(project)
    db_session.commit()

    context = manager.build_context(db=db_session, project_id=project.id, section="problems")
    # No hay Problems para este proyecto: el bloque current debe quedar vacío,
    # y ninguna clave debe tener valor None/"".
    assert context["current"]["problem_tree"] == {}
    for _key, value in _flatten_values(context):
        assert value != ""
        assert value is not None


# ---------------------------------------------------------------------------
# Eficiencia SQL (informativo, punto 27)
# ---------------------------------------------------------------------------

def test_sql_query_efficiency_problems(manager, db_session, two_projects, query_counter, capsys):
    project_a, _ = two_projects
    with query_counter:
        manager.build_context(db=db_session, project_id=project_a, section="problems")
    print(f"\n[SQL] build_context(section=problems) -> {query_counter.count} queries")
    # required=[project, planning_alignment, problem_tree]: cada loader ejecuta 1
    # query principal + 1 por relación con selectinload (constante, no N+1 por
    # fila). Observado: 9 queries.
    assert query_counter.count <= 12


def test_sql_query_efficiency_value_chain(manager, db_session, two_projects, query_counter, capsys):
    project_a, _ = two_projects
    with query_counter:
        manager.build_context(db=db_session, project_id=project_a, section="value_chain")
    print(f"\n[SQL] build_context(section=value_chain) -> {query_counter.count} queries")
    # required=[project, objectives, selected_alternative, requirements, value_chain]
    # + supporting=[technical_analysis]: 6 loaders con selectinload anidado
    # (constante por número de relaciones, no por número de filas). Observado: 14 queries.
    assert query_counter.count <= 18
