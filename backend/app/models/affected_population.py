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

FIELD_LABELS = {"region": "Región",
                "department": "Departamento",
                "city": "Ciudad",
                "population_center": "Centro Poblacional",
                "location_entity": "Entidad de Ubicación"}

# ──────────────────────── MODELO SQLALCHEMY ────────────────────────
class AffectedPopulation(Base):
    __tablename__ = "affected_population"
    __table_args__ = {
        "info": {
            "label_plural": "Población Afectada",
            "label_singular": "Población Afectada",
        }
    }

    id = Column(Integer, primary_key=True, index=True)
    region = Column(Text, nullable=False, info={"label": FIELD_LABELS["region"]})
    department = Column(String, nullable=False, info={"label": FIELD_LABELS["department"]})  # Corrige: era Integer pero representas texto
    city = Column(Text, nullable=True, info={"label": FIELD_LABELS["city"]})
    population_center = Column(Text, nullable=True, info={"label": FIELD_LABELS["population_center"]})
    location_entity = Column(Text, nullable=True, info={"label": FIELD_LABELS["location_entity"]})

    population_id = Column(Integer, ForeignKey("population.id"), nullable=False)
    population = relationship("Population", back_populates="affected_population")

# ──────────────────────── ESQUEMAS PYDANTIC ────────────────────────

class AffectedPopulationBase(BaseModel):
    region: str
    department: str
    city: Optional[str] = None
    population_center: Optional[str] = None
    location_entity: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)  # pydantic v2+

class AffectedPopulationCreate(AffectedPopulationBase):
    population_id: int

class AffectedPopulationResponse(AffectedPopulationBase):
    id: int
    population_id: int

# ──────────────────────── ROUTER FASTAPI ────────────────────────

router = APIRouter()

@router.post("/", response_model=AffectedPopulationResponse)
def create_affected_population(affected_population: AffectedPopulationCreate, db: Session = Depends(get_db)):
    from app.models.population import Population

    parent = db.query(Population).filter(Population.id == affected_population.population_id).first()
    if not parent:
        raise HTTPException(status_code=400, detail="Population with given ID does not exist")

    db_affected_population = AffectedPopulation(**affected_population.dict())
    db.add(db_affected_population)
    db.commit()
    db.refresh(db_affected_population)
    return db_affected_population

@router.get("/", response_model=List[AffectedPopulationResponse])
def get_affected_populations(db: Session = Depends(get_db)):
    return db.query(AffectedPopulation).all()

@router.get("/{affected_population_id}", response_model=AffectedPopulationResponse)
def get_affected_population(affected_population_id: int, db: Session = Depends(get_db)):
    result = db.query(AffectedPopulation).filter(AffectedPopulation.id == affected_population_id).first()
    if not result:
        raise HTTPException(status_code=404, detail="Affected population not found")
    return result

@router.delete("/{affected_population_id}", response_model=dict)
def delete_affected_population(affected_population_id: int, db: Session = Depends(get_db)):
    affected_population = db.query(AffectedPopulation).filter(AffectedPopulation.id == affected_population_id).first()
    if not affected_population:
        raise HTTPException(status_code=404, detail="Affected Population not found")
    
    db.delete(affected_population)
    db.commit()
    return {"message": "Affected Population deleted"}

@router.put("/{affected_population_id}", response_model=AffectedPopulationResponse)
def update_affected_population(affected_population_id: int, updated_data: AffectedPopulationCreate, db: Session = Depends(get_db)):
    affected_population = db.query(AffectedPopulation).filter(AffectedPopulation.id == affected_population_id).first()
    if not affected_population:
        raise HTTPException(status_code=404, detail="Affected Population not found")

    for key, value in updated_data.dict().items():
        setattr(affected_population, key, value)

    db.commit()
    db.refresh(affected_population)
    return affected_population
