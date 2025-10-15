from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, relationship
from app.core.database import Base, SessionLocal
from sqlalchemy import Column, Integer, Boolean, ForeignKey
from pydantic import BaseModel, ConfigDict
from typing import List, Optional

from app.models.alternatives import (
    Alternatives,
    AlternativesCreate,
    AlternativesResponse,
)

# ----------------------------
# Conexión a la DB
# ----------------------------
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ----------------------------
# Modelo SQLAlchemy
# ----------------------------
class AlternativesGeneral(Base):
    __tablename__ = "alternatives_general"

    id = Column(Integer, primary_key=True, index=True)
    solution_alternatives = Column(Boolean, nullable=False, default=False)
    cost = Column(Boolean, nullable=False, default=False)
    profitability = Column(Boolean, nullable=False, default=False)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False, unique=True)
    project = relationship("Project", back_populates="alternatives_general")

    alternatives = relationship(
        "Alternatives",
        back_populates="alternative",
        cascade="all, delete-orphan",
    )


# ----------------------------
# Esquemas Pydantic
# ----------------------------
class AlternativesGeneralBase(BaseModel):
    solution_alternatives: bool
    cost: bool
    profitability: bool

    model_config = ConfigDict(from_attributes=True)


class AlternativesGeneralCreate(AlternativesGeneralBase):
    alternatives: List[AlternativesCreate] = []


class AlternativesGeneralUpdate(BaseModel):
    solution_alternatives: Optional[bool] = None
    cost: Optional[bool] = None
    profitability: Optional[bool] = None
    alternatives: Optional[List[AlternativesCreate]] = None

    model_config = ConfigDict(from_attributes=True)


class AlternativesGeneralResponse(AlternativesGeneralBase):
    id: int
    project_id: int
    alternatives: List[AlternativesResponse] = []

    class Config:
        from_attributes = True  # ✅ Equivalente a orm_mode


# ----------------------------
# Rutas de FastAPI
# ----------------------------
router = APIRouter()


@router.post("/", response_model=AlternativesGeneralResponse)
def create_alternative(alternative: AlternativesGeneralCreate, db: Session = Depends(get_db)):
    db_alternative = AlternativesGeneral(**alternative.dict())
    db.add(db_alternative)
    db.commit()
    db.refresh(db_alternative)
    return db_alternative


@router.get("/", response_model=List[AlternativesGeneralResponse])
def get_alternatives(db: Session = Depends(get_db)):
    return db.query(AlternativesGeneral).all()


@router.get("/{project_id}", response_model=AlternativesGeneralResponse)
def get_alternative(project_id: int, db: Session = Depends(get_db)):
    alternative = db.query(AlternativesGeneral).filter(AlternativesGeneral.project_id == project_id).first()
    if not alternative:
        raise HTTPException(status_code=404, detail="Alternative not found")
    return alternative


@router.put("/{project_id}", response_model=AlternativesGeneralResponse)
def update_alternative(project_id: int, updated: AlternativesGeneralUpdate, db: Session = Depends(get_db)):
    alternative = db.query(AlternativesGeneral).filter(AlternativesGeneral.project_id == project_id).first()
    if not alternative:
        raise HTTPException(status_code=404, detail="Alternative not found")

    updated_data = updated.dict(exclude_unset=True)
    for key, value in updated_data.items():
        setattr(alternative, key, value)

    db.commit()
    db.refresh(alternative)
    return alternative


@router.delete("/{project_id}")
def delete_alternative(project_id: int, db: Session = Depends(get_db)):
    alternative = db.query(AlternativesGeneral).filter(AlternativesGeneral.project_id == project_id).first()
    if not alternative:
        raise HTTPException(status_code=404, detail="Alternative not found")

    db.delete(alternative)
    db.commit()
    return {"message": "Alternative deleted successfully"}
