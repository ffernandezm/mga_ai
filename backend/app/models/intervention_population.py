from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import relationship, Session
from app.core.database import Base, SessionLocal
from sqlalchemy import Column, Integer, String, Text, ForeignKey
from pydantic import BaseModel, ConfigDict
from typing import List, Optional

# ──────────────────────── DB SESSION ────────────────────────
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ──────────────────────── MODELO SQLALCHEMY ────────────────────────
class InterventionPopulation(Base):
    __tablename__ = "intervention_population"

    id = Column(Integer, primary_key=True, index=True)
    region = Column(Text, nullable=False)
    department = Column(String, nullable=False)  # Corrige: era Integer pero representas texto
    city = Column(Text, nullable=True)
    population_center = Column(Text, nullable=True)
    location_entity = Column(Text, nullable=True)

    population_id = Column(Integer, ForeignKey("population.id"), nullable=False)
    population = relationship("Population", back_populates="intervention_population")

# ──────────────────────── ESQUEMAS PYDANTIC ────────────────────────

class InterventionPopulationBase(BaseModel):
    region: str
    department: str
    city: Optional[str] = None
    population_center: Optional[str] = None
    location_entity: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)  # pydantic v2+

class InterventionPopulationCreate(InterventionPopulationBase):
    population_id: int

class InterventionPopulationResponse(InterventionPopulationBase):
    id: int
    population_id: int

# ──────────────────────── ROUTER FASTAPI ────────────────────────

router = APIRouter()

@router.post("/", response_model=InterventionPopulationResponse)
def create_intervention_population(intervention_population: InterventionPopulationCreate, db: Session = Depends(get_db)):
    from app.models.population import Population

    parent = db.query(Population).filter(Population.id == intervention_population.population_id).first()
    if not parent:
        raise HTTPException(status_code=400, detail="Population with given ID does not exist")

    db_intervention_population = InterventionPopulation(**intervention_population.dict())
    db.add(db_intervention_population)
    db.commit()
    db.refresh(db_intervention_population)
    return db_intervention_population

@router.get("/", response_model=List[InterventionPopulationResponse])
def get_intervention_populations(db: Session = Depends(get_db)):
    return db.query(InterventionPopulation).all()

@router.get("/{intervention_population_id}", response_model=InterventionPopulationResponse)
def get_intervention_population(intervention_population_id: int, db: Session = Depends(get_db)):
    result = db.query(InterventionPopulation).filter(InterventionPopulation.id == intervention_population_id).first()
    if not result:
        raise HTTPException(status_code=404, detail="Affected population not found")
    return result

@router.delete("/{intervention_population_id}", response_model=dict)
def delete_intervention_population(intervention_population_id: int, db: Session = Depends(get_db)):
    intervention_population = db.query(InterventionPopulation).filter(InterventionPopulation.id == intervention_population_id).first()
    if not intervention_population:
        raise HTTPException(status_code=404, detail="Affected Population not found")
    
    db.delete(intervention_population)
    db.commit()
    return {"message": "Affected Population deleted"}

@router.put("/{intervention_population_id}", response_model=InterventionPopulationResponse)
def update_intervention_population(intervention_population_id: int, updated_data: InterventionPopulationCreate, db: Session = Depends(get_db)):
    intervention_population = db.query(InterventionPopulation).filter(InterventionPopulation.id == intervention_population_id).first()
    if not intervention_population:
        raise HTTPException(status_code=404, detail="Affected Population not found")

    for key, value in updated_data.dict().items():
        setattr(intervention_population, key, value)

    db.commit()
    db.refresh(intervention_population)
    return intervention_population
