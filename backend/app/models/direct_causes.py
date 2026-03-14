from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel
from sqlalchemy import Column, ForeignKey, Integer, Text
from sqlalchemy.orm import Session, relationship

from app.core.database import Base, SessionLocal

# Conexión a la DB
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Importar modelos relacionados para objectives_causes
from app.models.objectives_causes import ObjectivesCauses
from app.models.objectives import Objectives
from app.models.indirect_causes import IndirectCause as IndirectCauseModel


# =========================
# MODELO SQLALCHEMY
# =========================
class DirectCause(Base):
    __tablename__ = "direct_causes"

    id = Column(Integer, primary_key=True, index=True)
    problem_id = Column(Integer, ForeignKey("problems.id", ondelete="CASCADE"))
    description = Column(Text)

    problem = relationship("Problems", back_populates="direct_causes")
    indirect_causes = relationship(
        "IndirectCause",
        back_populates="direct_cause",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )


# Importamos esquemas y modelo del hijo para creación anidada
from app.models.indirect_causes import (  # noqa: E402
    IndirectCause as IndirectCauseModel,
    IndirectCauseCreate,
    IndirectCauseResponse,
)

# =========================
# ESQUEMAS Pydantic
# =========================
class DirectCauseBase(BaseModel):
    description: str


class DirectCauseCreate(DirectCauseBase):
    indirect_causes: List[IndirectCauseCreate] = []


class DirectCauseUpdate(BaseModel):
    description: Optional[str] = None


class DirectCauseResponse(DirectCauseBase):
    id: int
    indirect_causes: List[IndirectCauseResponse] = []

    class Config:
        from_attributes = True


# =========================
# ROUTER
# =========================
router = APIRouter()


def _get_direct_cause_or_404(
    db: Session, direct_cause_id: int, problem_id: Optional[int] = None
) -> DirectCause:
    q = db.query(DirectCause).filter(DirectCause.id == direct_cause_id)
    if problem_id is not None:
        q = q.filter(DirectCause.problem_id == problem_id)
    obj = q.first()
    if not obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="DirectCause no encontrado."
        )
    return obj


@router.get(
    "/{problem_id}",
    response_model=List[DirectCauseResponse],
    summary="Listar causas directas por problem_id",
)
def list_direct_causes(
    problem_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db),
):
    items = (
        db.query(DirectCause)
        .filter(DirectCause.problem_id == problem_id)
        .offset(skip)
        .limit(limit)
        .all()
    )
    return items


@router.post(
    "/{problem_id}",
    response_model=DirectCauseResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Crear una causa directa (opcionalmente con causas indirectas)",
)
def create_direct_cause(
    problem_id: int, payload: DirectCauseCreate, db: Session = Depends(get_db)
):
    obj = DirectCause(problem_id=problem_id, description=payload.description)
    db.add(obj)
    db.flush()  # Obtener ID para hijos

    # Obtener el objective del proyecto
    from app.models.problems import Problems
    problem = db.query(Problems).filter(Problems.id == problem_id).first()
    objective = None
    if problem:
        objective = db.query(Objectives).filter(Objectives.project_id == problem.project_id).first()

    for child in payload.indirect_causes or []:
        indirect_obj = IndirectCauseModel(
            direct_cause_id=obj.id,
            description=child.description,
        )
        db.add(indirect_obj)
        db.flush()  # Obtener ID

        # Crear registro en objectives_causes para la indirecta
        if objective:
            obj_causes_indirect = ObjectivesCauses(
                type="indirecta",
                cause_related=indirect_obj.description,
                specifics_objectives=None,
                objective_id=objective.id,
                cause_id=indirect_obj.id
            )
            db.add(obj_causes_indirect)
            db.commit()

    # Crear registro en objectives_causes para la directa
    if objective:
        obj_causes = ObjectivesCauses(
            type="directa",
            cause_related=obj.description,
            specifics_objectives=None,
            objective_id=objective.id,
            cause_id=obj.id
        )
        db.add(obj_causes)
        db.commit()

    db.refresh(obj)
    return obj


@router.get(
    "/{problem_id}/{direct_cause_id}",
    response_model=DirectCauseResponse,
    summary="Obtener causa directa por ID dentro de un problem_id",
)
def get_direct_cause(
    problem_id: int, direct_cause_id: int, db: Session = Depends(get_db)
):
    obj = _get_direct_cause_or_404(db, direct_cause_id, problem_id=problem_id)
    return obj


@router.put(
    "/{problem_id}/{direct_cause_id}",
    response_model=DirectCauseResponse,
    summary="Actualizar una causa directa (solo campos propios)",
)
def update_direct_cause(
    problem_id: int,
    direct_cause_id: int,
    payload: DirectCauseUpdate,
    db: Session = Depends(get_db),
):
    obj = _get_direct_cause_or_404(db, direct_cause_id, problem_id=problem_id)

    if payload.description is not None:
        old_description = obj.description
        obj.description = payload.description

        # Actualizar en objectives_causes y en value_chain_objectives si corresponde
        from app.models.problems import Problems
        problem = db.query(Problems).filter(Problems.id == problem_id).first()
        if problem:
            objective = db.query(Objectives).filter(Objectives.project_id == problem.project_id).first()
            if objective:
                # Buscar registro de objectives_causes correspondiente
                obj_causes = db.query(ObjectivesCauses).filter(
                    ObjectivesCauses.cause_id == obj.id,
                    ObjectivesCauses.type == "directa",
                ).first()
                if obj_causes:
                    obj_causes.cause_related = obj.description
                    # si existe un value_chain_objective ligado, no lo actualizamos aquí porque el
                    # nombre de vc_obj se deriva de specifics_objectives, no de la descripción
                    # de la causa. Solo lo haremos si especificamos explícitamente un mapping
                    # futuro.


    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete(
    "/{problem_id}/{direct_cause_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Eliminar una causa directa",
)
def delete_direct_cause(
    problem_id: int, direct_cause_id: int, db: Session = Depends(get_db)
):
    obj = _get_direct_cause_or_404(db, direct_cause_id, problem_id=problem_id)

    # Eliminar en objectives_causes (y cascada a value_chain_objectives)
    from app.models.problems import Problems
    from app.models.value_chain_objectives import ValueChainObjectives
    problem = db.query(Problems).filter(Problems.id == problem_id).first()
    if problem:
        objective = db.query(Objectives).filter(Objectives.project_id == problem.project_id).first()
        if objective:
            # Buscar el registro de objectives_causes correspondiente
            obj_causes = db.query(ObjectivesCauses).filter(
                ObjectivesCauses.cause_id == obj.id,
                ObjectivesCauses.type == "directa",
            ).first()
            if obj_causes:
                # Si hay un value_chain_objective asociado, eliminarlo también
                if obj_causes.value_chain_objective_id:
                    vc_obj = db.query(ValueChainObjectives).filter(
                        ValueChainObjectives.id == obj_causes.value_chain_objective_id
                    ).first()
                    if vc_obj:
                        db.delete(vc_obj)
                db.delete(obj_causes)

    db.delete(obj)
    db.commit()
    return None
