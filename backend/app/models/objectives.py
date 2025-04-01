from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import Base, SessionLocal
from sqlalchemy import Column, Integer, Text
from pydantic import BaseModel
from typing import List

# Conexión a la DB
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Modelo en SQLAlchemy
class Objectives(Base):
    __tablename__ = "objectives"

    id = Column(Integer, primary_key=True, index=True)
    general_objective = Column(Text)
    cause_relations = Column(Text)

# Esquema Pydantic
class ObjectivesBase(BaseModel):
    general_objective: str
    cause_relations: str

class ObjectivesCreate(ObjectivesBase):
    pass

class ObjectivesResponse(ObjectivesBase):
    id: int

    class Config:
        from_attributes  = True

# Rutas de FastAPI
router = APIRouter()

@router.post("/", response_model=ObjectivesResponse)
def create_objective(objective: ObjectivesCreate, db: Session = Depends(get_db)):
    db_objective = Objectives(**objective.dict())
    db.add(db_objective)
    db.commit()
    db.refresh(db_objective)
    return db_objective

@router.get("/", response_model=List[ObjectivesResponse])
def get_objectives(db: Session = Depends(get_db)):
    return db.query(Objectives).all()
