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
class Population(Base):
    __tablename__ = "population"

    id = Column(Integer, primary_key=True, index=True)
    affected_population = Column(Text)
    target_population = Column(Text)
    demographic_characteristics = Column(Text)

# Esquema Pydantic
class PopulationBase(BaseModel):
    affected_population: str
    target_population: str
    demographic_characteristics: str

class PopulationCreate(PopulationBase):
    pass

class PopulationResponse(PopulationBase):
    id: int

    class Config:
        from_attributes  = True

# Rutas de FastAPI
router = APIRouter()

@router.post("/", response_model=PopulationResponse)
def create_population(population: PopulationCreate, db: Session = Depends(get_db)):
    db_population = Population(**population.dict())
    db.add(db_population)
    db.commit()
    db.refresh(db_population)
    return db_population

@router.get("/", response_model=List[PopulationResponse])
def get_population(db: Session = Depends(get_db)):
    return db.query(Population).all()
