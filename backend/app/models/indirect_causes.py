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
class IndirectCause(Base):
    __tablename__ = "indirect_causes"

    id = Column(Integer, primary_key=True, index=True)
    direct_cause_id = Column(Integer, ForeignKey("direct_causes.id", ondelete="CASCADE"))
    description = Column(Text)

    direct_cause = relationship("DirectCause", back_populates="indirect_causes")


# =========================
# ESQUEMAS Pydantic
# =========================
class IndirectCauseBase(BaseModel):
    description: str


class IndirectCauseCreate(IndirectCauseBase):
    pass


class IndirectCauseUpdate(BaseModel):
    description: Optional[str] = None


class IndirectCauseResponse(IndirectCauseBase):
    id: int

    class Config:
        from_attributes = True


# =========================
# ROUTER
# =========================
router = APIRouter()


def _get_indirect_cause_or_404(
    db: Session, indirect_cause_id: int, direct_cause_id: Optional[int] = None
) -> IndirectCause:
    q = db.query(IndirectCause).filter(IndirectCause.id == indirect_cause_id)
    if direct_cause_id is not None:
        q = q.filter(IndirectCause.direct_cause_id == direct_cause_id)
    obj = q.first()
    if not obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="IndirectCause no encontrado."
        )
    return obj


@router.get(
    "/{direct_cause_id}",
    response_model=List[IndirectCauseResponse],
    summary="Listar causas indirectas por direct_cause_id",
)
def list_indirect_causes(
    direct_cause_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db),
):
    items = (
        db.query(IndirectCause)
        .filter(IndirectCause.direct_cause_id == direct_cause_id)
        .offset(skip)
        .limit(limit)
        .all()
    )
    return items


@router.post(
    "/{direct_cause_id}",
    response_model=IndirectCauseResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Crear una causa indirecta para una causa directa",
)
def create_indirect_cause(
    direct_cause_id: int, payload: IndirectCauseCreate, db: Session = Depends(get_db)
):
    obj = IndirectCause(
        direct_cause_id=direct_cause_id, description=payload.description
    )
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.get(
    "/{direct_cause_id}/{indirect_cause_id}",
    response_model=IndirectCauseResponse,
    summary="Obtener una causa indirecta por ID dentro de una causa directa",
)
def get_indirect_cause(
    direct_cause_id: int, indirect_cause_id: int, db: Session = Depends(get_db)
):
    obj = _get_indirect_cause_or_404(
        db, indirect_cause_id, direct_cause_id=direct_cause_id
    )
    return obj


@router.put(
    "/{direct_cause_id}/{indirect_cause_id}",
    response_model=IndirectCauseResponse,
    summary="Actualizar una causa indirecta",
)
def update_indirect_cause(
    direct_cause_id: int,
    indirect_cause_id: int,
    payload: IndirectCauseUpdate,
    db: Session = Depends(get_db),
):
    obj = _get_indirect_cause_or_404(
        db, indirect_cause_id, direct_cause_id=direct_cause_id
    )

    if payload.description is not None:
        obj.description = payload.description

    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete(
    "/{direct_cause_id}/{indirect_cause_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Eliminar una causa indirecta",
)
def delete_indirect_cause(
    direct_cause_id: int, indirect_cause_id: int, db: Session = Depends(get_db)
):
    obj = _get_indirect_cause_or_404(
        db, indirect_cause_id, direct_cause_id=direct_cause_id
    )
    db.delete(obj)
    db.commit()
    return None
