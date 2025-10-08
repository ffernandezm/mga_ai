from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, relationship
from app.core.database import Base, SessionLocal
from sqlalchemy import Column, Integer, Boolean
from pydantic import BaseModel, ConfigDict
from typing import List

from app.models.alternatives import (
    Alternatives,
    AlternativesCreate,
    AlternativesResponse,
)

# Conexión a la DB
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Modelo en SQLAlchemy
class AlternativesGeneral(Base):
    __tablename__ = "alternatives_general"

    id = Column(Integer, primary_key=True, index=True)
    solution_alternatives = Column(Boolean, nullable=False, default=False)
    cost = Column(Boolean, nullable=False, default=False)
    profitability = Column(Boolean, nullable=False, default=False)
    
    alternatives = relationship(
        "Alternatives",
        back_populates="alternative",
        cascade="all, delete-orphan",
    )

# Esquemas Pydantic
class AlternativesGeneralBase(BaseModel):
    solution_alternatives: bool
    cost: bool
    profitability: bool
    
    model_config = ConfigDict(from_attributes=True)

class AlternativesGeneralCreate(AlternativesGeneralBase):
    alternatives: List[AlternativesCreate] = []

class AlternativesGeneralResponse(AlternativesGeneralBase):
    id: int
    
    alternatives: List[AlternativesResponse] = []

    class Config:
        from_attributes = True  # ✅ equivale a orm_mode

# Rutas de FastAPI
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

@router.get("/{id}", response_model=AlternativesGeneralResponse)
def get_alternative(id: int, db: Session = Depends(get_db)):
    alternative = db.query(AlternativesGeneral).filter(AlternativesGeneral.id == id).first()
    if not alternative:
        raise HTTPException(status_code=404, detail="Alternative not found")
    return alternative

@router.put("/{id}", response_model=AlternativesGeneralResponse)
def update_alternative(id: int, updated: AlternativesGeneralCreate, db: Session = Depends(get_db)):
    alternative = db.query(AlternativesGeneral).filter(AlternativesGeneral.id == id).first()
    if not alternative:
        raise HTTPException(status_code=404, detail="Alternative not found")
    for key, value in updated.dict().items():
        setattr(alternative, key, value)
    db.commit()
    db.refresh(alternative)
    return alternative

@router.delete("/{id}")
def delete_alternative(id: int, db: Session = Depends(get_db)):
    alternative = db.query(AlternativesGeneral).filter(AlternativesGeneral.id == id).first()
    if not alternative:
        raise HTTPException(status_code=404, detail="Alternative not found")
    db.delete(alternative)
    db.commit()
    return {"message": "Alternative deleted successfully"}
