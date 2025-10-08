from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, relationship
from app.core.database import SessionLocal, Base
from sqlalchemy import Column, Integer, Text, Float, ForeignKey
from pydantic import BaseModel, Field
from typing import List



# Conexión a la DB
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Modelo en SQLAlchemy
class ObjectivesIndicator(Base):
    __tablename__ = "objectives_indicator"

    id = Column(Integer, primary_key=True, index=True)
    indicator = Column(Text, nullable=False)
    unit = Column(Text, nullable=False)
    meta = Column(Float, nullable=False, default=0.0)
    source_type = Column(Text, nullable=False)
    source_validation = Column(Text, nullable=False)
    
    objective_id = Column(Integer, ForeignKey("objectives.id"))
    objective = relationship("Objectives", back_populates="objectives_indicators")

# Esquemas Pydantic
class ObjectivesIndicatorBase(BaseModel):
    indicator: str = Field(..., min_length=3, max_length=255)
    unit: str = Field(..., min_length=1, max_length=50)
    meta: float | None = Field(0.0, ge=0)
    source_type: str = Field(..., min_length=3, max_length=100)
    source_validation: str = Field(..., min_length=3, max_length=255)

class ObjectivesIndicatorCreate(ObjectivesIndicatorBase):
    objective_id: int

class ObjectivesIndicatorResponse(ObjectivesIndicatorBase):
    id: int
    objective_id: int

    class Config:
        from_attributes = True  # ✅ equivale a orm_mode

# Rutas de FastAPI
router = APIRouter()

@router.post("/", response_model=ObjectivesIndicatorResponse)
def create_objective_indicators(objective: ObjectivesIndicatorCreate, db: Session = Depends(get_db)):
    db_objective = ObjectivesIndicator(**objective.dict())
    db.add(db_objective)
    db.commit()
    db.refresh(db_objective)
    return db_objective

@router.get("/", response_model=List[ObjectivesIndicatorResponse])
def get_objectives_indicators(db: Session = Depends(get_db)):
    return db.query(ObjectivesIndicator).all()

@router.get("/{id}", response_model=ObjectivesIndicatorResponse)
def get_objective_indicator(id: int, db: Session = Depends(get_db)):
    objective = db.query(ObjectivesIndicator).filter(ObjectivesIndicator.id == id).first()
    if not objective:
        raise HTTPException(status_code=404, detail="Objective indicator not found")
    return objective

@router.put("/{id}", response_model=ObjectivesIndicatorResponse)
def update_objective_indicator(id: int, updated: ObjectivesIndicatorCreate, db: Session = Depends(get_db)):
    objective = db.query(ObjectivesIndicator).filter(ObjectivesIndicator.id == id).first()
    if not objective:
        raise HTTPException(status_code=404, detail="Objective indicator not found")
    for key, value in updated.dict().items():
        setattr(objective, key, value)
    db.commit()
    db.refresh(objective)
    return objective

@router.delete("/{id}")
def delete_objective_indicator(id: int, db: Session = Depends(get_db)):
    objective = db.query(ObjectivesIndicator).filter(ObjectivesIndicator.id == id).first()
    if not objective:
        raise HTTPException(status_code=404, detail="Objective indicator not found")
    db.delete(objective)
    db.commit()
    return {"message": "Objective indicator deleted successfully"}
