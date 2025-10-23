from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel
from sqlalchemy import Column, ForeignKey, Integer, Text
from sqlalchemy.orm import Session, relationship

from app.core.database import Base, SessionLocal

# =========================
# Conexión a la DB (get_db)
# =========================
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


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

    for child in payload.indirect_causes or []:
        db.add(
            IndirectCauseModel(
                direct_cause_id=obj.id,
                description=child.description,
            )
        )

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
        obj.description = payload.description

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
    db.delete(obj)
    db.commit()
    return None
