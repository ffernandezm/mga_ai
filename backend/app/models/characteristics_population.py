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
class CharacteristicsPopulation(Base):
    __tablename__ = "characteristics_population"

    id = Column(Integer, primary_key=True, index=True)
    classification = Column(Text, nullable=False)
    detail = Column(String, nullable=False)  # Corrige: era Integer pero representas texto
    people_number = Column(Integer, nullable=False) 
    information = Column(Text, nullable=True)


    population_id = Column(Integer, ForeignKey("population.id"), nullable=False)
    population = relationship("Population", back_populates="characteristics_population")

# ──────────────────────── ESQUEMAS PYDANTIC ────────────────────────

class CharacteristicsPopulationBase(BaseModel):
    classification: str
    detail: Optional[str] = None
    people_number: Optional[int] = None
    information: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)

class CharacteristicsPopulationCreate(CharacteristicsPopulationBase):
    population_id: int

class CharacteristicsPopulationResponse(CharacteristicsPopulationBase):
    id: int
    population_id: int

# ──────────────────────── ROUTER FASTAPI ────────────────────────

router = APIRouter()

@router.post("/", response_model=CharacteristicsPopulationResponse)
def create_characteristics_population(characteristics_population: CharacteristicsPopulationCreate, db: Session = Depends(get_db)):
    from app.models.population import Population

    parent = db.query(Population).filter(Population.id == characteristics_population.population_id).first()
    if not parent:
        raise HTTPException(status_code=400, detail="Population with given ID does not exist")

    db_characteristics_population = CharacteristicsPopulation(**characteristics_population.dict())
    db.add(db_characteristics_population)
    db.commit()
    db.refresh(db_characteristics_population)
    return db_characteristics_population

@router.get("/", response_model=List[CharacteristicsPopulationResponse])
def get_characteristics_populations(db: Session = Depends(get_db)):
    return db.query(CharacteristicsPopulation).all()

@router.get("/{characteristics_population_id}", response_model=CharacteristicsPopulationResponse)
def get_characteristics_population(characteristics_population_id: int, db: Session = Depends(get_db)):
    result = db.query(CharacteristicsPopulation).filter(CharacteristicsPopulation.id == characteristics_population_id).first()
    if not result:
        raise HTTPException(status_code=404, detail="Characteristics population not found")
    return result

@router.delete("/{characteristics_population_id}", response_model=dict)
def delete_characteristics_population(characteristics_population_id: int, db: Session = Depends(get_db)):
    characteristics_population = db.query(CharacteristicsPopulation).filter(CharacteristicsPopulation.id == characteristics_population_id).first()
    if not characteristics_population:
        raise HTTPException(status_code=404, detail="Characteristics Population not found")
    
    db.delete(characteristics_population)
    db.commit()
    return {"message": "Characteristics Population deleted"}

@router.put("/{characteristics_population_id}", response_model=CharacteristicsPopulationResponse)
def update_characteristics_population(characteristics_population_id: int, updated_data: CharacteristicsPopulationCreate, db: Session = Depends(get_db)):
    characteristics_population = db.query(CharacteristicsPopulation).filter(CharacteristicsPopulation.id == characteristics_population_id).first()
    if not characteristics_population:
        raise HTTPException(status_code=404, detail="Characteristics Population not found")

    for key, value in updated_data.dict().items():
        setattr(characteristics_population, key, value)

    db.commit()
    db.refresh(characteristics_population)
    return characteristics_population
