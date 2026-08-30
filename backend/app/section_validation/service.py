from dataclasses import dataclass, field
from typing import Callable, Dict, List

from sqlalchemy.orm import Session, joinedload

from app.ai.context.module_dependencies import normalize_section
from app.models.activity import Activity
from app.models.alternatives_general import AlternativesGeneral
from app.models.development_plans import DevelopmentPlans
from app.models.direct_causes import DirectCause
from app.models.direct_effects import DirectEffect
from app.models.localization_general import LocalizationGeneral
from app.models.objectives import Objectives
from app.models.participants_general import ParticipantsGeneral
from app.models.population import Population
from app.models.problems import Problems
from app.models.product import Product
from app.models.requirements_general import RequirementsGeneral
from app.models.technical_analysis import TechnicalAnalysis
from app.models.value_chain import ValueChain
from app.models.value_chain_objectives import ValueChainObjectives

from .schemas import BlockingRule, MissingField, SectionStatus, SectionValidationResult
from .section_rules import SECTION_ORDER, SECTION_PREREQUISITES


def _has_text(value: object) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _missing(key: str, label: str, path: str) -> MissingField:
    return MissingField(key=key, label=label, path=path)


@dataclass
class _ValidationData:
    started: bool
    missing: List[MissingField] = field(default_factory=list)
    blocking: List[BlockingRule] = field(default_factory=list)


class SectionValidationService:
    """Fuente canónica de completitud de las secciones de formulación."""

    def __init__(self, db: Session):
        self.db = db
        self._validators: Dict[str, Callable[[int], _ValidationData]] = {
            "development_plans": self._validate_development_plans,
            "problems": self._validate_problems,
            "participants": self._validate_participants,
            "population": self._validate_population,
            "objectives": self._validate_objectives,
            "alternatives": self._validate_alternatives,
            "requirements": self._validate_requirements,
            "technical_analysis": self._validate_technical_analysis,
            "localization": self._validate_localization,
            "value_chain": self._validate_value_chain,
        }

    def validate_section(self, project_id: int, section: str, include_prerequisites: bool = True) -> SectionValidationResult:
        canonical = normalize_section(section)
        data = self._validators[canonical](project_id)
        incomplete_prerequisites = []
        if include_prerequisites:
            for prerequisite in SECTION_PREREQUISITES[canonical]:
                result = self.validate_section(project_id, prerequisite, False)
                if not result.complete:
                    incomplete_prerequisites.append(prerequisite)
        prerequisites_complete = not incomplete_prerequisites
        complete = not data.missing and not data.blocking
        status = (
            SectionStatus.BLOCKED if not prerequisites_complete else
            SectionStatus.COMPLETE if complete else
            SectionStatus.IN_PROGRESS if data.started else
            SectionStatus.NOT_STARTED
        )
        return SectionValidationResult(
            section=canonical,
            status=status,
            complete=complete,
            missing_fields=data.missing,
            blocking_rules=data.blocking,
            prerequisites_complete=prerequisites_complete,
            incomplete_prerequisites=incomplete_prerequisites,
        )

    def validate_all(self, project_id: int) -> List[SectionValidationResult]:
        return [self.validate_section(project_id, section) for section in SECTION_ORDER]

    def _validate_development_plans(self, project_id: int) -> _ValidationData:
        plan = self.db.query(DevelopmentPlans).filter_by(project_id=project_id).first()
        missing = []
        if not plan or not _has_text(plan.national_development_plan):
            missing.append(_missing("national_development_plan", "Articulación con el PND", "development_plans.national_development_plan"))
        if not plan or not _has_text(plan.program):
            missing.append(_missing("program", "Programa relacionado", "development_plans.program"))
        if plan:
            groups = (
                ("departmental_or_sectoral_development_plan", "strategy_departmental", "program_departmental", "departamental o sectorial"),
                ("district_or_municipal_development_plan", "strategy_district", "program_district", "distrital o municipal"),
                ("other_development_plan", "strategy_other", "program_other", "otro plan"),
            )
            for plan_key, strategy_key, program_key, label in groups:
                if _has_text(getattr(plan, plan_key)):
                    if not _has_text(getattr(plan, strategy_key)):
                        missing.append(_missing(strategy_key, f"Estrategia del plan {label}", f"development_plans.{strategy_key}"))
                    if not _has_text(getattr(plan, program_key)):
                        missing.append(_missing(program_key, f"Programa del plan {label}", f"development_plans.{program_key}"))
        return _ValidationData(plan is not None, missing)

    def _validate_problems(self, project_id: int) -> _ValidationData:
        problem = (
            self.db.query(Problems)
            .options(
                joinedload(Problems.direct_causes),
                joinedload(Problems.direct_effects),
            )
            .filter(Problems.project_id == project_id)
            .first()
        )
        values = {
            "central_problem": getattr(problem, "central_problem", None),
            "current_description": getattr(problem, "current_description", None),
            "magnitude_problem": getattr(problem, "magnitude_problem", None),
        }
        specs = {
            "central_problem": ("Problema central", "problems.central_problem"),
            "current_description": (
                "Descripción de la situación existente",
                "problems.current_description",
            ),
            "magnitude_problem": (
                "Indicador o magnitud actual del problema",
                "problems.magnitude_problem",
            ),
        }
        missing = [
            _missing(key, label, path)
            for key, (label, path) in specs.items()
            if not _has_text(values[key])
        ]

        causes = list(problem.direct_causes) if problem else []
        effects = list(problem.direct_effects) if problem else []
        if not causes:
            missing.append(
                _missing("direct_causes", "Al menos una causa directa", "direct_causes")
            )
        for cause in causes:
            if not _has_text(cause.description):
                missing.append(
                    _missing(f"direct_causes.{cause.id}.description", "Descripción de la causa directa", f"direct_causes.{cause.id}.description")
                )

        if not effects:
            missing.append(
                _missing("direct_effects", "Al menos un efecto directo", "direct_effects")
            )
        for effect in effects:
            if not _has_text(effect.description):
                missing.append(
                    _missing(f"direct_effects.{effect.id}.description", "Descripción del efecto directo", f"direct_effects.{effect.id}.description")
                )
        return _ValidationData(problem is not None, missing)

    def _validate_participants(self, project_id: int) -> _ValidationData:
        general = self.db.query(ParticipantsGeneral).filter_by(project_id=project_id).first()
        participants = list(general.participants) if general else []
        missing = []
        if not general or not _has_text(general.participants_analisis):
            missing.append(_missing("participants_analisis", "Análisis general de participantes", "participants_general.participants_analisis"))
        if not participants:
            missing.append(_missing("participants", "Al menos un participante", "participants"))
        for participant in participants:
            prefix = f"participants.{participant.id}"
            if not (_has_text(participant.participant_actor) or _has_text(participant.participant_entity)):
                missing.append(_missing(f"{prefix}.actor", "Actor, persona o entidad", f"{prefix}.participant_actor"))
            if not _has_text(participant.rol):
                missing.append(_missing(f"{prefix}.rol", "Posición o rol", f"{prefix}.rol"))
            if not _has_text(participant.interest_expectative):
                missing.append(_missing(f"{prefix}.interest_expectative", "Intereses y expectativas", f"{prefix}.interest_expectative"))
            role = (participant.rol or "").strip().lower()
            if role in {"beneficiario", "cooperante", "oponente", "perjudicado"} and not _has_text(participant.contribution_conflicts):
                label = "Contribución" if role in {"beneficiario", "cooperante"} else "Estrategia de gestión"
                missing.append(_missing(f"{prefix}.contribution_conflicts", label, f"{prefix}.contribution_conflicts"))
        return _ValidationData(general is not None, missing)

    def _validate_population(self, project_id: int) -> _ValidationData:
        population = self.db.query(Population).filter_by(project_id=project_id).first()
        missing = []
        specs = (
            ("population_number_affected", "Cantidad de población afectada", False),
            ("population_info_affected", "Fuente e información de población afectada", True),
            ("population_number_intervention", "Cantidad de población objetivo", False),
            ("population_info_intervention", "Fuente y criterio de población objetivo", True),
        )
        for key, label, text in specs:
            value = getattr(population, key, None)
            if (text and not _has_text(value)) or (not text and value is None):
                missing.append(_missing(key, label, f"population.{key}"))
        blocking = []
        if population:
            affected = population.population_number_affected
            target = population.population_number_intervention
            if (affected is not None and affected < 0) or (target is not None and target < 0):
                blocking.append(BlockingRule(key="population.non_negative", message="Las cantidades de población no pueden ser negativas."))
            if affected is not None and target is not None and target > affected:
                blocking.append(BlockingRule(key="population.target_lte_affected", message="La población objetivo no puede superar la población afectada."))
        return _ValidationData(population is not None, missing, blocking)

    def _validate_objectives(self, project_id: int) -> _ValidationData:
        objective = self.db.query(Objectives).filter_by(project_id=project_id).first()
        missing = []
        if not objective or not _has_text(objective.general_objective):
            missing.append(_missing("general_objective", "Objetivo general", "objectives.general_objective"))
        causes = list(objective.objectives_causes) if objective else []
        if not any(_has_text(item.specifics_objectives) for item in causes):
            missing.append(_missing("specific_objectives", "Al menos un objetivo específico", "objectives_causes.specifics_objectives"))
        indicators = list(objective.objectives_indicators) if objective else []
        if not indicators:
            missing.append(_missing("objectives_indicators", "Indicador de resultado y meta", "objectives_indicators"))
        for indicator in indicators:
            if not _has_text(indicator.indicator):
                missing.append(_missing(f"objectives_indicators.{indicator.id}.indicator", "Indicador de resultado", f"objectives_indicators.{indicator.id}.indicator"))
            if indicator.meta is None:
                missing.append(_missing(f"objectives_indicators.{indicator.id}.meta", "Meta del indicador", f"objectives_indicators.{indicator.id}.meta"))
        direct_causes = self.db.query(DirectCause).join(Problems).filter(Problems.project_id == project_id).all()
        linked_ids = {item.cause_id for item in causes if item.cause_id is not None and _has_text(item.specifics_objectives)}
        unlinked = [cause for cause in direct_causes if cause.id not in linked_ids]
        blocking = []
        if unlinked:
            blocking.append(BlockingRule(key="objectives.direct_causes_coverage", message=f"{len(unlinked)} causa(s) directa(s) no tienen un objetivo específico asociado."))
        problem = self.db.query(Problems).filter_by(project_id=project_id).first()
        if objective and problem and (objective.general_problem or "").strip() != (problem.central_problem or "").strip():
            blocking.append(BlockingRule(key="objectives.problem_match", message="El objetivo general no está asociado al problema central vigente."))
        return _ValidationData(objective is not None, missing, blocking)

    def _validate_alternatives(self, project_id: int) -> _ValidationData:
        general = self.db.query(AlternativesGeneral).filter_by(project_id=project_id).first()
        alternatives = list(general.alternatives) if general else []
        missing = []
        if not alternatives:
            missing.append(_missing("alternatives", "Al menos una alternativa", "alternatives"))
        for alternative in alternatives:
            if not _has_text(alternative.name):
                missing.append(_missing(f"alternatives.{alternative.id}.name", "Nombre o descripción de la alternativa", f"alternatives.{alternative.id}.name"))
        active_count = sum(1 for alternative in alternatives if alternative.active)
        blocking = [] if active_count == 1 else [BlockingRule(key="alternatives.exactly_one_active", message="Debe existir exactamente una alternativa activa para continuar a Necesidades.")]
        return _ValidationData(general is not None, missing, blocking)

    def _validate_requirements(self, project_id: int) -> _ValidationData:
        general = self.db.query(RequirementsGeneral).filter_by(project_id=project_id).first()
        requirements = list(general.requirements) if general else []
        missing = []
        if not general or not _has_text(general.requirements_analysis):
            missing.append(_missing("requirements_analysis", "Análisis de necesidades", "requirements_general.requirements_analysis"))
        if not requirements:
            missing.append(_missing("requirements", "Al menos un bien o servicio", "requirements"))
        fields = (("good_service_name", "Bien o servicio", True), ("unit_of_measure", "Unidad de medida", True), ("supply_description", "Información de oferta", True), ("demand_description", "Información de demanda", True), ("start_year", "Año de inicio", False), ("end_year", "Año de fin", False), ("last_projected_year", "Último año proyectado", False))
        blocking = []
        for requirement in requirements:
            for key, label, text in fields:
                value = getattr(requirement, key)
                if (text and not _has_text(value)) or (not text and value is None):
                    missing.append(_missing(f"requirements.{requirement.id}.{key}", label, f"requirements.{requirement.id}.{key}"))
            if requirement.start_year and requirement.end_year and requirement.end_year < requirement.start_year:
                blocking.append(BlockingRule(key=f"requirements.{requirement.id}.year_range", message="El año de fin no puede ser anterior al año de inicio."))
            if requirement.end_year and requirement.last_projected_year and requirement.last_projected_year < requirement.end_year:
                blocking.append(BlockingRule(key=f"requirements.{requirement.id}.projection_range", message="El último año proyectado debe cubrir el horizonte definido."))
        return _ValidationData(general is not None, missing, blocking)

    def _validate_technical_analysis(self, project_id: int) -> _ValidationData:
        analysis = self.db.query(TechnicalAnalysis).filter_by(project_id=project_id).first()
        missing = [] if analysis and _has_text(analysis.analysis) else [_missing("analysis", "Descripción y requisitos del análisis técnico", "technical_analysis.analysis")]
        return _ValidationData(analysis is not None, missing)

    def _validate_localization(self, project_id: int) -> _ValidationData:
        general = self.db.query(LocalizationGeneral).filter_by(project_id=project_id).first()
        localizations = list(general.localizations) if general else []
        missing = []
        if not localizations:
            missing.append(_missing("localizations", "Localización de la alternativa", "localization"))
        for localization in localizations:
            for key, label in (("region", "Región"), ("department", "Departamento"), ("city", "Municipio o ciudad")):
                if not _has_text(getattr(localization, key)):
                    missing.append(_missing(f"localization.{localization.id}.{key}", label, f"localization.{localization.id}.{key}"))
            if localization.georeferencing and (localization.latitude is None or localization.longitude is None):
                missing.append(_missing(f"localization.{localization.id}.coordinates", "Coordenadas de la localización", f"localization.{localization.id}.latitude"))
        return _ValidationData(general is not None, missing)

    def _validate_value_chain(self, project_id: int) -> _ValidationData:
        chains = self.db.query(ValueChain).filter_by(project_id=project_id).all()
        objectives = self.db.query(ValueChainObjectives).filter_by(project_id=project_id).all()
        products = self.db.query(Product).filter_by(project_id=project_id).all()
        activities = self.db.query(Activity).filter_by(project_id=project_id).all()
        missing = []
        if not chains:
            missing.append(_missing("value_chains", "Cadena de valor", "value_chains"))
        if not objectives:
            missing.append(_missing("value_chain_objectives", "Objetivo específico de la cadena de valor", "value_chain_objectives"))
        if not products:
            missing.append(_missing("products", "Al menos un producto", "products"))
        blocking = []
        objective_ids = {objective.id for objective in objectives}
        product_ids = {product.id for product in products}
        for product in products:
            if product.value_chain_objective_id not in objective_ids:
                blocking.append(BlockingRule(key=f"products.{product.id}.objective", message="Existe un producto sin objetivo de cadena válido."))
            if not _has_text(product.name):
                missing.append(_missing(f"products.{product.id}.name", "Nombre del producto", f"products.{product.id}.name"))
            related = [activity for activity in activities if activity.product_id == product.id]
            if len(related) < 2:
                blocking.append(BlockingRule(key=f"products.{product.id}.activities", message=f"El producto '{product.name or product.id}' debe tener al menos dos actividades."))
        for activity in activities:
            if activity.product_id not in product_ids:
                blocking.append(BlockingRule(key=f"activities.{activity.id}.product", message="Existe una actividad sin producto válido."))
            if not _has_text(activity.description):
                missing.append(_missing(f"activities.{activity.id}.description", "Descripción de la actividad", f"activities.{activity.id}.description"))
        return _ValidationData(bool(chains or objectives or products or activities), missing, blocking)