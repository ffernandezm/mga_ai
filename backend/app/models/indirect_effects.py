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
class IndirectEffect(Base):
    __tablename__ = "indirect_effects"

    id = Column(Integer, primary_key=True, index=True)
    direct_effect_id = Column(Integer, ForeignKey("direct_effects.id", ondelete="CASCADE"))
    description = Column(Text)

    direct_effect = relationship("DirectEffect", back_populates="indirect_effects")


# =========================
# ESQUEMAS Pydantic
# =========================
class IndirectEffectBase(BaseModel):
    description: str


class IndirectEffectCreate(IndirectEffectBase):
    pass


class IndirectEffectUpdate(BaseModel):
    description: Optional[str] = None


class IndirectEffectResponse(IndirectEffectBase):
    id: int

    class Config:
        from_attributes = True


# =========================
# ROUTER
# =========================
router = APIRouter()


def _get_indirect_effect_or_404(
    db: Session, indirect_effect_id: int, direct_effect_id: Optional[int] = None
) -> IndirectEffect:
    q = db.query(IndirectEffect).filter(IndirectEffect.id == indirect_effect_id)
    if direct_effect_id is not None:
        q = q.filter(IndirectEffect.direct_effect_id == direct_effect_id)
    obj = q.first()
    if not obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="IndirectEffect no encontrado."
        )
    return obj


@router.get(
    "/{direct_effect_id}",
    response_model=List[IndirectEffectResponse],
    summary="Listar efectos indirectos por direct_effect_id",
)
def list_indirect_effects(
    direct_effect_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db),
):
    items = (
        db.query(IndirectEffect)
        .filter(IndirectEffect.direct_effect_id == direct_effect_id)
        .offset(skip)
        .limit(limit)
        .all()
    )
    return items


@router.post(
    "/{direct_effect_id}",
    response_model=IndirectEffectResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Crear un efecto indirecto para un direct_effect",
)
def create_indirect_effect(
    direct_effect_id: int, payload: IndirectEffectCreate, db: Session = Depends(get_db)
):
    obj = IndirectEffect(
        direct_effect_id=direct_effect_id, description=payload.description
    )
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.get(
    "/{direct_effect_id}/{indirect_effect_id}",
    response_model=IndirectEffectResponse,
    summary="Obtener un efecto indirecto por ID dentro de un direct_effect",
)
def get_indirect_effect(
    direct_effect_id: int, indirect_effect_id: int, db: Session = Depends(get_db)
):
    obj = _get_indirect_effect_or_404(
        db, indirect_effect_id, direct_effect_id=direct_effect_id
    )
    return obj


@router.put(
    "/{direct_effect_id}/{indirect_effect_id}",
    response_model=IndirectEffectResponse,
    summary="Actualizar un efecto indirecto",
)
def update_indirect_effect(
    direct_effect_id: int,
    indirect_effect_id: int,
    payload: IndirectEffectUpdate,
    db: Session = Depends(get_db),
):
    obj = _get_indirect_effect_or_404(
        db, indirect_effect_id, direct_effect_id=direct_effect_id
    )

    if payload.description is not None:
        obj.description = payload.description

    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete(
    "/{direct_effect_id}/{indirect_effect_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Eliminar un efecto indirecto",
)
def delete_indirect_effect(
    direct_effect_id: int, indirect_effect_id: int, db: Session = Depends(get_db)
):
    obj = _get_indirect_effect_or_404(
        db, indirect_effect_id, direct_effect_id=direct_effect_id
    )
    db.delete(obj)
    db.commit()
    return None
