"""Loaders SQLAlchemy reales para construir objetos semánticos MGA por project_id.

Cada loader recibe (db, project_id, cache) y devuelve una estructura Python
(dict/list) ya limpia de ids internos y de columnas *_json. NUNCA devuelve
instancias ORM crudas.

`cache` es un dict compartido durante una sola llamada a
`ContextManager.build_semantic_context(...)`, usado para evitar volver a
consultar objetos ya cargados (p. ej. "problem_summary" se deriva de
"problem_tree" sin una query adicional).

Limitaciones documentadas explícitamente:
- `pnd_details.selected_to_project` es global (la tabla no tiene project_id),
  por lo que NO se usa aquí. `load_planning_alignment` solo usa
  `development_plans`/`pnds`, que sí tienen project_id.
- `product_catalogs.selected_to_project` también es global (sin project_id).
  `load_value_chain` usa `products.project_id` para aislar por proyecto.
"""

from __future__ import annotations

import logging
from typing import Any, Callable, Dict, List, Optional

from sqlalchemy.orm import Session, selectinload

from app.models.activity import Activity
from app.models.alternatives_general import AlternativesGeneral
from app.models.direct_causes import DirectCause
from app.models.direct_effects import DirectEffect
from app.models.development_plans import DevelopmentPlans
from app.models.localization_general import LocalizationGeneral
from app.models.objectives import Objectives
from app.models.participants_general import ParticipantsGeneral
from app.models.population import Population
from app.models.problems import Problems
from app.models.product import Product
from app.models.project import Project
from app.models.requirements_general import RequirementsGeneral
from app.models.technical_analysis import TechnicalAnalysis
from app.models.value_chain import ValueChain
from app.models.value_chain_objectives import ValueChainObjectives
from .select_domains import get_select_metadata

Cache = Dict[str, Any]

logger = logging.getLogger(__name__)


def _drop_empty(data: Dict[str, Any]) -> Dict[str, Any]:
    """Elimina None/""/[]/{} pero conserva booleanos y números (incl. 0/False)."""
    return {k: v for k, v in data.items() if not (v is None or v == "" or v == [] or v == {})}


def _drop_empty_list(items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    return [item for item in items if item]


# ---------------------------------------------------------------------------
# project
# ---------------------------------------------------------------------------

def load_project(db: Session, project_id: int, cache: Optional[Cache] = None) -> Dict[str, Any]:
    project = (
        db.query(Project)
        .options(selectinload(Project.project_localizations))
        .filter(Project.id == project_id)
        .first()
    )
    if not project:
        return {}

    data = _drop_empty(
        {
            "name": project.name,
            "description": project.description,
            "process": project.process,
            "object_desc": project.object_desc,
            "intervention_type": project.intervention_type,
            "project_typology": project.project_typology,
            "main_product": project.main_product,
            "sector": project.sector,
        }
    )

    locations = _drop_empty_list(
        [
            _drop_empty(
                {
                    "region": loc.region,
                    "department": loc.department,
                    "municipality": loc.municipality,
                }
            )
            for loc in project.project_localizations
        ]
    )
    if locations:
        data["locations"] = locations
    return data


# ---------------------------------------------------------------------------
# planning_alignment (development_plans + pnds)
# ---------------------------------------------------------------------------

def load_planning_alignment(db: Session, project_id: int, cache: Optional[Cache] = None) -> Dict[str, Any]:
    plan = (
        db.query(DevelopmentPlans)
        .options(selectinload(DevelopmentPlans.pnds))
        .filter(DevelopmentPlans.project_id == project_id)
        .first()
    )
    if not plan:
        return {}

    data = _drop_empty(
        {
            "program": plan.program,
            "national_development_plan": plan.national_development_plan,
            "departmental_or_sectoral_development_plan": plan.departmental_or_sectoral_development_plan,
            "strategy_departmental": plan.strategy_departmental,
            "program_departmental": plan.program_departmental,
            "district_or_municipal_development_plan": plan.district_or_municipal_development_plan,
            "strategy_district": plan.strategy_district,
            "program_district": plan.program_district,
            "community_type": plan.community_type,
            "ethnic_group_planning_instruments": plan.ethnic_group_planning_instruments,
            "other_development_plan": plan.other_development_plan,
            "strategy_other": plan.strategy_other,
            "program_other": plan.program_other,
        }
    )

    pnds = _drop_empty_list(
        [
            _drop_empty(
                {
                    "transformation": p.transformation,
                    "pillar": p.pillar,
                    "catalyst": p.catalyst,
                    "component": p.component,
                }
            )
            for p in plan.pnds
        ]
    )
    if pnds:
        data["national_plan_details"] = pnds
    # NOTA: pnd_details NO se incluye aquí: es una tabla global sin project_id.
    return data


# ---------------------------------------------------------------------------
# problem_tree / problem_summary
# ---------------------------------------------------------------------------

def load_problem_tree(db: Session, project_id: int, cache: Optional[Cache] = None) -> Dict[str, Any]:
    if cache is not None and "problem_tree" in cache:
        return cache["problem_tree"]

    problem = (
        db.query(Problems)
        .options(
            selectinload(Problems.direct_causes).selectinload(DirectCause.indirect_causes),
            selectinload(Problems.direct_effects).selectinload(DirectEffect.indirect_effects),
        )
        .filter(Problems.project_id == project_id)
        .first()
    )

    result: Dict[str, Any] = {}
    if problem:
        result = _drop_empty(
            {
                "central_problem": problem.central_problem,
                "current_description": problem.current_description,
                "magnitude_problem": problem.magnitude_problem,
            }
        )

        direct_causes = []
        for dc in problem.direct_causes:
            entry = _drop_empty({"description": dc.description})
            indirect = _drop_empty_list([_drop_empty({"description": ic.description}) for ic in dc.indirect_causes])
            if indirect:
                entry["indirect_causes"] = indirect
            if entry:
                direct_causes.append(entry)
        if direct_causes:
            result["direct_causes"] = direct_causes

        direct_effects = []
        for de in problem.direct_effects:
            entry = _drop_empty({"description": de.description})
            indirect = _drop_empty_list([_drop_empty({"description": ie.description}) for ie in de.indirect_effects])
            if indirect:
                entry["indirect_effects"] = indirect
            if entry:
                direct_effects.append(entry)
        if direct_effects:
            result["direct_effects"] = direct_effects

    if cache is not None:
        cache["problem_tree"] = result
    return result


def load_problem_summary(db: Session, project_id: int, cache: Optional[Cache] = None) -> Dict[str, Any]:
    tree = cache.get("problem_tree") if cache is not None else None
    if tree is None:
        tree = load_problem_tree(db, project_id, cache)
    if not tree:
        return {}

    summary = {k: tree[k] for k in ("central_problem", "current_description", "magnitude_problem") if k in tree}
    if "direct_causes" in tree:
        descriptions = [dc.get("description") for dc in tree["direct_causes"] if dc.get("description")]
        if descriptions:
            summary["direct_causes"] = descriptions
    if "direct_effects" in tree:
        descriptions = [de.get("description") for de in tree["direct_effects"] if de.get("description")]
        if descriptions:
            summary["direct_effects"] = descriptions
    return summary


# ---------------------------------------------------------------------------
# participants / participants_summary
# ---------------------------------------------------------------------------

def load_participants(db: Session, project_id: int, cache: Optional[Cache] = None) -> Dict[str, Any]:
    if cache is not None and "participants" in cache:
        return cache["participants"]

    pg = (
        db.query(ParticipantsGeneral)
        .options(selectinload(ParticipantsGeneral.participants))
        .filter(ParticipantsGeneral.project_id == project_id)
        .first()
    )

    result: Dict[str, Any] = {}
    if pg:
        result = _drop_empty({"participants_analisis": pg.participants_analisis})
        actors = _drop_empty_list(
            [
                _drop_empty(
                    {
                        "participant_actor": p.participant_actor,
                        "participant_entity": p.participant_entity,
                        "interest_expectative": p.interest_expectative,
                        "rol": p.rol,
                        "contribution_conflicts": p.contribution_conflicts,
                    }
                )
                for p in pg.participants
            ]
        )
        if actors:
            result["actors"] = actors
        result["select_fields"] = [
            get_select_metadata("participant_actor"),
            get_select_metadata("participant_entity"),
            get_select_metadata("rol"),
        ]

    if cache is not None:
        cache["participants"] = result
    return result


def load_participants_summary(db: Session, project_id: int, cache: Optional[Cache] = None) -> Dict[str, Any]:
    participants = cache.get("participants") if cache is not None else None
    if participants is None:
        participants = load_participants(db, project_id, cache)
    actors = participants.get("actors", []) if participants else []
    if not actors:
        return {}

    summary = _drop_empty_list(
        [
            _drop_empty(
                {
                    "participant_actor": a.get("participant_actor"),
                    "participant_entity": a.get("participant_entity"),
                    "rol": a.get("rol"),
                    "interest_expectative": a.get("interest_expectative"),
                }
            )
            for a in actors
        ]
    )
    return {"actors": summary} if summary else {}


# ---------------------------------------------------------------------------
# population / population_summary / intervention_population
# ---------------------------------------------------------------------------

def load_population(db: Session, project_id: int, cache: Optional[Cache] = None) -> Dict[str, Any]:
    if cache is not None and "population" in cache:
        return cache["population"]

    pop = (
        db.query(Population)
        .options(
            selectinload(Population.affected_population),
            selectinload(Population.intervention_population),
            selectinload(Population.characteristics_population),
        )
        .filter(Population.project_id == project_id)
        .first()
    )

    result: Dict[str, Any] = {}
    if pop:
        affected = _drop_empty(
            {
                "type": pop.population_type_affected,
                "number": pop.population_number_affected,
                "information": pop.population_info_affected,
            }
        )
        affected_locations = _drop_empty_list(
            [
                _drop_empty(
                    {
                        "region": loc.region,
                        "department": loc.department,
                        "city": loc.city,
                        "population_center": loc.population_center,
                        "location_entity": loc.location_entity,
                    }
                )
                for loc in pop.affected_population
            ]
        )
        if affected_locations:
            affected["locations"] = affected_locations

        intervention = _drop_empty(
            {
                "type": pop.population_type_intervention,
                "number": pop.population_number_intervention,
                "information": pop.population_info_intervention,
            }
        )
        intervention_locations = _drop_empty_list(
            [
                _drop_empty(
                    {
                        "region": loc.region,
                        "department": loc.department,
                        "city": loc.city,
                        "population_center": loc.population_center,
                        "location_entity": loc.location_entity,
                    }
                )
                for loc in pop.intervention_population
            ]
        )
        if intervention_locations:
            intervention["locations"] = intervention_locations

        characteristics = _drop_empty_list(
            [
                _drop_empty(
                    {
                        "classification": c.classification,
                        "detail": c.detail,
                        "people_number": c.people_number,
                        "information": c.information,
                    }
                )
                for c in pop.characteristics_population
            ]
        )

        if affected:
            result["affected"] = affected
        if intervention:
            result["intervention"] = intervention
        if characteristics:
            result["characteristics"] = characteristics

    if cache is not None:
        cache["population"] = result
    return result


def load_population_summary(db: Session, project_id: int, cache: Optional[Cache] = None) -> Dict[str, Any]:
    pop = cache.get("population") if cache is not None else None
    if pop is None:
        pop = load_population(db, project_id, cache)
    if not pop:
        return {}

    summary: Dict[str, Any] = {}
    if "affected" in pop:
        entry = _drop_empty({"type": pop["affected"].get("type"), "number": pop["affected"].get("number")})
        if entry:
            summary["affected"] = entry
    if "intervention" in pop:
        entry = _drop_empty({"type": pop["intervention"].get("type"), "number": pop["intervention"].get("number")})
        if entry:
            summary["intervention"] = entry

    locations = pop.get("intervention", {}).get("locations") or pop.get("affected", {}).get("locations")
    if locations:
        summary["main_locations"] = locations[:3]
    return summary


def load_intervention_population(db: Session, project_id: int, cache: Optional[Cache] = None) -> Dict[str, Any]:
    pop = cache.get("population") if cache is not None else None
    if pop is None:
        pop = load_population(db, project_id, cache)
    intervention = pop.get("intervention") if pop else None
    if not intervention:
        return {}

    return _drop_empty(
        {
            "population_type_intervention": intervention.get("type"),
            "population_number_intervention": intervention.get("number"),
            "population_info_intervention": intervention.get("information"),
            "locations": intervention.get("locations", []),
        }
    )


# ---------------------------------------------------------------------------
# objectives / objectives_summary
# ---------------------------------------------------------------------------

def load_objectives(db: Session, project_id: int, cache: Optional[Cache] = None) -> Dict[str, Any]:
    if cache is not None and "objectives" in cache:
        return cache["objectives"]

    obj = (
        db.query(Objectives)
        .options(
            selectinload(Objectives.objectives_causes),
            selectinload(Objectives.objectives_indicators),
        )
        .filter(Objectives.project_id == project_id)
        .first()
    )

    result: Dict[str, Any] = {}
    if obj:
        result = _drop_empty({"general_objective": obj.general_objective})

        # Evitar duplicar el problema central si general_problem es un espejo textual.
        problem_tree = cache.get("problem_tree") if cache is not None else None
        central_problem = problem_tree.get("central_problem") if problem_tree else None
        if obj.general_problem and obj.general_problem != central_problem:
            result["general_problem"] = obj.general_problem

        specific_objectives = _drop_empty_list(
            [
                _drop_empty(
                    {
                        "cause_related": oc.cause_related,
                        "type": oc.type,
                        "objective": oc.specifics_objectives,
                    }
                )
                for oc in obj.objectives_causes
            ]
        )
        if specific_objectives:
            result["specific_objectives"] = specific_objectives

        indicators = _drop_empty_list(
            [
                _drop_empty(
                    {
                        "indicator": oi.indicator,
                        "unit": oi.unit,
                        "meta": oi.meta,
                        "source_type": oi.source_type,
                        "source_validation": oi.source_validation,
                    }
                )
                for oi in obj.objectives_indicators
            ]
        )
        if indicators:
            result["indicators"] = indicators

    if cache is not None:
        cache["objectives"] = result
    return result


def load_objectives_summary(db: Session, project_id: int, cache: Optional[Cache] = None) -> Dict[str, Any]:
    obj = cache.get("objectives") if cache is not None else None
    if obj is None:
        obj = load_objectives(db, project_id, cache)
    if not obj:
        return {}

    summary: Dict[str, Any] = {}
    if "general_objective" in obj:
        summary["general_objective"] = obj["general_objective"]
    if "specific_objectives" in obj:
        objectives_only = [so.get("objective") for so in obj["specific_objectives"] if so.get("objective")]
        if objectives_only:
            summary["specific_objectives"] = objectives_only
    return summary


# ---------------------------------------------------------------------------
# alternatives (TODAS las alternativas registradas) / selected_alternative
# ---------------------------------------------------------------------------

def load_alternatives(db: Session, project_id: int, cache: Optional[Cache] = None) -> List[Dict[str, Any]]:
    """Devuelve TODAS las alternativas registradas del proyecto (no solo la activa).

    Objeto "current" de la sección `alternatives` (ver task 22/registro de
    secciones). `selected_alternative` es un objeto semántico separado,
    usado por secciones posteriores (requirements, technical_analysis,
    localization, value_chain).
    """
    ag = (
        db.query(AlternativesGeneral)
        .options(selectinload(AlternativesGeneral.alternatives))
        .filter(AlternativesGeneral.project_id == project_id)
        .first()
    )
    if not ag or not ag.alternatives:
        return []

    return _drop_empty_list(
        [
            _drop_empty({"name": a.name, "state": a.state, "active": a.active})
            for a in ag.alternatives
        ]
    )


def load_selected_alternative(db: Session, project_id: int, cache: Optional[Cache] = None) -> Dict[str, Any]:
    """Expone alternativas disponibles sin inferir selección MGA desde `active`."""
    alternatives = load_alternatives(db, project_id, cache)
    return {"alternatives": alternatives} if alternatives else {}


# ---------------------------------------------------------------------------
# requirements
# ---------------------------------------------------------------------------

def load_requirements(db: Session, project_id: int, cache: Optional[Cache] = None) -> Dict[str, Any]:
    if cache is not None and "requirements" in cache:
        return cache["requirements"]

    rg = (
        db.query(RequirementsGeneral)
        .options(selectinload(RequirementsGeneral.requirements))
        .filter(RequirementsGeneral.project_id == project_id)
        .first()
    )

    result: Dict[str, Any] = {}
    if rg:
        result = _drop_empty({"requirements_analysis": rg.requirements_analysis})
        goods_services = _drop_empty_list(
            [
                _drop_empty(
                    {
                        "name": r.good_service_name,
                        "description": r.good_service_description,
                        "supply_description": r.supply_description,
                        "demand_description": r.demand_description,
                        "unit_of_measure": r.unit_of_measure,
                        "start_year": r.start_year,
                        "end_year": r.end_year,
                        "last_projected_year": r.last_projected_year,
                    }
                )
                for r in rg.requirements
            ]
        )
        if goods_services:
            result["goods_services"] = goods_services

    if cache is not None:
        cache["requirements"] = result
    return result


# ---------------------------------------------------------------------------
# technical_analysis
# ---------------------------------------------------------------------------

def load_technical_analysis(db: Session, project_id: int, cache: Optional[Cache] = None) -> Dict[str, Any]:
    ta = db.query(TechnicalAnalysis).filter(TechnicalAnalysis.project_id == project_id).first()
    if not ta or not ta.analysis:
        return {}
    return {"analysis": ta.analysis}


# ---------------------------------------------------------------------------
# localization
# ---------------------------------------------------------------------------

_LOCALIZATION_FACTOR_LABELS: Dict[str, str] = {
    "administrative_political_factors": "Factores Político-Administrativos",
    "proximity_to_target_population": "Proximidad a la población objetivo",
    "proximity_to_supply_sources": "Proximidad a fuentes de abastecimiento",
    "communications": "Comunicaciones",
    "land_cost_and_availability": "Costo y disponibilidad de terreno",
    "public_services_availability": "Disponibilidad de servicios públicos",
    "labor_availability_and_cost": "Disponibilidad y costo de mano de obra",
    "tax_and_legal_structure": "Estructura fiscal y legal",
    "environmental_factors": "Factores ambientales",
    "gender_equity_impact": "Impacto en la equidad de género",
    "transport_means_and_costs": "Medios de transporte y costos",
    "public_order": "Orden público",
    "other_factors": "Otros factores",
    "topography": "Topografía",
}


def load_localization(db: Session, project_id: int, cache: Optional[Cache] = None) -> Dict[str, Any]:
    lg = (
        db.query(LocalizationGeneral)
        .options(selectinload(LocalizationGeneral.localizations))
        .filter(LocalizationGeneral.project_id == project_id)
        .first()
    )
    if not lg:
        return {}

    result: Dict[str, Any] = {}
    locations = _drop_empty_list(
        [
            _drop_empty(
                {
                    "region": loc.region,
                    "department": loc.department,
                    "city": loc.city,
                    "type_group": loc.type_group,
                    "group": loc.group,
                    "entity": loc.entity,
                    "georeferencing": loc.georeferencing,
                    "latitude": loc.latitude,
                    "longitude": loc.longitude,
                }
            )
            for loc in lg.localizations
        ]
    )
    if locations:
        result["locations"] = locations

    # Solo se listan las etiquetas de factores con valor True (evitar ruido de "false").
    active_factors = [label for field, label in _LOCALIZATION_FACTOR_LABELS.items() if getattr(lg, field, False)]
    if active_factors:
        result["active_factors"] = active_factors

    return result


# ---------------------------------------------------------------------------
# value_chain
# ---------------------------------------------------------------------------

def load_value_chain(db: Session, project_id: int, cache: Optional[Cache] = None) -> Dict[str, Any]:
    """Reconstruye la jerarquía real value_chain -> objectives -> products -> activities.

    Aislamiento por proyecto: se filtra por `products.project_id` /
    `activities.project_id`, NO por `product_catalogs.selected_to_project`
    (tabla global sin project_id).
    """
    chains = (
        db.query(ValueChain)
        .options(
            selectinload(ValueChain.value_chain_objectives)
            .selectinload(ValueChainObjectives.products)
            .selectinload(Product.activities)
        )
        .filter(ValueChain.project_id == project_id)
        .all()
    )
    if not chains:
        return {}

    chain_entries = []
    for chain in chains:
        objective_entries = []
        for vco in chain.value_chain_objectives:
            product_entries = []
            for prod in vco.products:
                if prod.project_id != project_id:
                    continue
                activity_entries = _drop_empty_list(
                    [
                        _drop_empty({"description": act.description, "cost": act.cost, "stage": act.stage})
                        for act in prod.activities
                        if act.project_id == project_id
                    ]
                )
                product_entry = _drop_empty(
                    {
                        "name": prod.name,
                        "description": prod.description,
                        "measured_through": prod.measured_through,
                        "quantity": prod.quantity,
                        "cost": prod.cost,
                        "stage": prod.stage,
                    }
                )
                if activity_entries:
                    product_entry["activities"] = activity_entries
                if product_entry:
                    product_entries.append(product_entry)

            objective_entry = _drop_empty({"name": vco.name})
            if product_entries:
                objective_entry["products"] = product_entries
            if objective_entry:
                objective_entries.append(objective_entry)

        chain_entry = _drop_empty({"name": chain.name})
        if objective_entries:
            chain_entry["objectives"] = objective_entries
        if chain_entry:
            chain_entries.append(chain_entry)

    if not chain_entries:
        return {}
    if len(chain_entries) == 1:
        return chain_entries[0]
    return {"chains": chain_entries}


LoaderFn = Callable[[Session, int, Optional[Cache]], Any]

SEMANTIC_LOADERS: Dict[str, LoaderFn] = {
    "project": load_project,
    "planning_alignment": load_planning_alignment,
    "problem_tree": load_problem_tree,
    "problem_summary": load_problem_summary,
    "participants": load_participants,
    "participants_summary": load_participants_summary,
    "population": load_population,
    "population_summary": load_population_summary,
    "objectives": load_objectives,
    "objectives_summary": load_objectives_summary,
    "alternatives": load_alternatives,
    "selected_alternative": load_selected_alternative,
    "requirements": load_requirements,
    "technical_analysis": load_technical_analysis,
    "intervention_population": load_intervention_population,
    "localization": load_localization,
    "value_chain": load_value_chain,
}
