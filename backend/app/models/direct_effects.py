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
class DirectEffect(Base):
    __tablename__ = "direct_effects"

    id = Column(Integer, primary_key=True, index=True)
    problem_id = Column(Integer, ForeignKey("problems.id", ondelete="CASCADE"))
    description = Column(Text)

    # Relaciones
    problem = relationship("Problems", back_populates="direct_effects")
    indirect_effects = relationship(
        "IndirectEffect",
        back_populates="direct_effect",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )


# Importamos esquemas y modelo del hijo para creación anidada
from app.models.indirect_effects import (  # noqa: E402
    IndirectEffect as IndirectEffectModel,
    IndirectEffectCreate,
    IndirectEffectResponse,
)

# =========================
# ESQUEMAS Pydantic
# =========================
class DirectEffectBase(BaseModel):
    description: str


class DirectEffectCreate(DirectEffectBase):
    indirect_effects: List[IndirectEffectCreate] = []


class DirectEffectUpdate(BaseModel):
    description: Optional[str] = None


class DirectEffectResponse(DirectEffectBase):
    id: int
    indirect_effects: List[IndirectEffectResponse] = []

    class Config:
        from_attributes = True


# =========================
# ROUTER
# =========================
router = APIRouter()


def _get_direct_effect_or_404(
    db: Session, direct_effect_id: int, problem_id: Optional[int] = None
) -> DirectEffect:
    q = db.query(DirectEffect).filter(DirectEffect.id == direct_effect_id)
    if problem_id is not None:
        q = q.filter(DirectEffect.problem_id == problem_id)
    obj = q.first()
    if not obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="DirectEffect no encontrado."
        )
    return obj


@router.get(
    "/{problem_id}",
    response_model=List[DirectEffectResponse],
    summary="Listar efectos directos por problem_id",
)
def list_direct_effects(
    problem_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db),
):
    items = (
        db.query(DirectEffect)
        .filter(DirectEffect.problem_id == problem_id)
        .offset(skip)
        .limit(limit)
        .all()
    )
    return items


@router.post(
    "/{problem_id}",
    response_model=DirectEffectResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Crear un efecto directo (opcionalmente con efectos indirectos)",
)
def create_direct_effect(
    problem_id: int, payload: DirectEffectCreate, db: Session = Depends(get_db)
):
    obj = DirectEffect(problem_id=problem_id, description=payload.description)
    db.add(obj)
    db.flush()  # Obtener ID antes de agregar hijos

    for child in payload.indirect_effects or []:
        db.add(
            IndirectEffectModel(
                direct_effect_id=obj.id,
                description=child.description,
            )
        )

    db.commit()
    db.refresh(obj)
    return obj


@router.get(
    "/{problem_id}/{direct_effect_id}",
    response_model=DirectEffectResponse,
    summary="Obtener efecto directo por ID dentro de un problem_id",
)
def get_direct_effect(
    problem_id: int, direct_effect_id: int, db: Session = Depends(get_db)
):
    obj = _get_direct_effect_or_404(db, direct_effect_id, problem_id=problem_id)
    return obj


@router.put(
    "/{problem_id}/{direct_effect_id}",
    response_model=DirectEffectResponse,
    summary="Actualizar un efecto directo (solo campos propios)",
)
def update_direct_effect(
    problem_id: int,
    direct_effect_id: int,
    payload: DirectEffectUpdate,
    db: Session = Depends(get_db),
):
    obj = _get_direct_effect_or_404(db, direct_effect_id, problem_id=problem_id)

    if payload.description is not None:
        obj.description = payload.description

    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete(
    "/{problem_id}/{direct_effect_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Eliminar un efecto directo",
)
def delete_direct_effect(
    problem_id: int, direct_effect_id: int, db: Session = Depends(get_db)
):
    obj = _get_direct_effect_or_404(db, direct_effect_id, problem_id=problem_id)
    db.delete(obj)
    db.commit()
    return None
