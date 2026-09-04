"""Sincronizacion determinista entre el arbol de problemas y objetivos_causes."""

from __future__ import annotations

from sqlalchemy.orm import Session, selectinload

from app.models.direct_causes import DirectCause
from app.models.indirect_causes import IndirectCause
from app.models.objectives_causes import ObjectivesCauses
from app.models.problems import Problems


def sync_objective_causes(db: Session, project_id: int) -> list[ObjectivesCauses]:
    """Alinea las relaciones de causas del objetivo con el arbol vigente."""
    problem = (
        db.query(Problems)
        .options(selectinload(Problems.direct_causes).selectinload(DirectCause.indirect_causes))
        .filter(Problems.project_id == project_id)
        .first()
    )
    # Import local para evitar el ciclo Objectives -> ObjectivesCauses -> modelos de causas.
    from app.models.objectives import Objectives

    objective = db.query(Objectives).filter(Objectives.project_id == project_id).first()
    if not objective:
        return []

    causes = []
    if problem:
        for direct in problem.direct_causes:
            causes.append((direct.id, "directa", direct.description or ""))
            causes.extend(
                (indirect.id, "indirecta", indirect.description or "")
                for indirect in direct.indirect_causes
            )

    existing = list(
        db.query(ObjectivesCauses)
        .filter(ObjectivesCauses.objective_id == objective.id)
        .all()
    )
    by_identity = {}
    duplicates = []
    for item in existing:
        key = (item.cause_id, (item.type or "").lower())
        if item.cause_id is not None and key in by_identity:
            duplicates.append(item)
        elif item.cause_id is not None:
            by_identity[key] = item
    legacy = [item for item in existing if item.cause_id is None]
    active_keys = set()
    synchronized = []

    for cause_id, cause_type, description in causes:
        key = (cause_id, cause_type)
        relation = by_identity.get(key)
        if relation is None and legacy:
            relation = next(
                (
                    item for item in legacy
                    if (item.type or "").lower() == cause_type
                    and (item.cause_related or "") == description
                ),
                None,
            )
            if relation:
                legacy.remove(relation)
        if relation is None:
            relation = ObjectivesCauses(
                objective_id=objective.id,
                cause_id=cause_id,
                type=cause_type,
                cause_related=description,
                specifics_objectives=None,
            )
            db.add(relation)
            db.flush()
        else:
            relation.cause_id = cause_id
            relation.type = cause_type
            relation.cause_related = description
        active_keys.add(key)
        synchronized.append(relation)

    for relation in existing:
        key = (relation.cause_id, (relation.type or "").lower())
        if key not in active_keys or relation in duplicates:
            db.delete(relation)

    db.flush()
    return synchronized
