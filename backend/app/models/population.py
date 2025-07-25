from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session, relationship
from app.core.database import Base, SessionLocal
from sqlalchemy import Column, Integer, Text, ForeignKey, JSON
from pydantic import BaseModel
from typing import List, Optional

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
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False, unique=True)
    
    project = relationship("Project", back_populates="population")
    # affected_population = relationship("affected_population", back_populates="population")
    # target_population = relationship("target_population", back_populates="population")
    # affected_popdemographic_characteristicsulation = relationship("demographic_characteristics", back_populates="population")
    
    population_json = Column(JSON, nullable=True)

# Esquema Pydantic
class PopulationBase(BaseModel):
    participants_json: Optional[dict] = None

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
