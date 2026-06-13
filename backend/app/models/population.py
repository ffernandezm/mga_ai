from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, relationship
from app.core.database import Base, SessionLocal
from sqlalchemy import Column, Integer, JSON,Text, ForeignKey
from pydantic import BaseModel
from typing import List, Optional


# Importamos los esquemas y el modelo de AffectedPopulation
from app.models.affected_population import (
    AffectedPopulation,
    AffectedPopulationCreate,
    AffectedPopulationResponse,
)

# Importamos los esquemas y el modelo de InterventionPopulation
from app.models.intervention_population import (
    InterventionPopulation,
    InterventionPopulationCreate,
    InterventionPopulationResponse,
)

from app.models.characteristics_population import (
    CharacteristicsPopulation,
    CharacteristicsPopulationCreate,
    CharacteristicsPopulationResponse,
)

# —————————————————————————————————————————
#  Conexión a la DB
# —————————————————————————————————————————
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

FIELD_LABELS = {"population_type_affected": "Tipo de Población Afectada",
                "population_number_affected": "Número de Población Afectada",
                "population_info_affected": "Información de Población Afectada",
                "population_type_intervention": "Tipo de Población de Intervención",
                "population_number_intervention": "Número de Población de Intervención",
                "population_info_intervention": "Información de Población de Intervención"}

# —————————————————————————————————————————
#  Modelo SQLAlchemy: Population
# —————————————————————————————————————————
class Population(Base):
    __tablename__ = "population"
    __table_args__ = {
        "info": {
            "label_plural": "Población",
            "label_singular": "Población",
        }
    }

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False, unique=True)

    # Relaciones
    project = relationship("Project", back_populates="population")
    
    population_type_affected = Column(Text, nullable=False, default="Personas", info={"label": FIELD_LABELS["population_type_affected"]})
    population_number_affected = Column(Integer, nullable=True, info={"label": FIELD_LABELS["population_number_affected"]})
    population_info_affected = Column(Text, nullable=True, info={"label": FIELD_LABELS["population_info_affected"]})
    affected_population = relationship(
        "AffectedPopulation",
        back_populates="population",
        cascade="all, delete-orphan",
    )
    
    population_type_intervention = Column(Text, nullable=False, default="Personas", info={"label": FIELD_LABELS["population_type_intervention"]})
    population_number_intervention = Column(Integer, nullable=True, info={"label": FIELD_LABELS["population_number_intervention"]})
    population_info_intervention = Column(Text, nullable=True, info={"label": FIELD_LABELS["population_info_intervention"]})
    intervention_population = relationship(
        "InterventionPopulation",
        back_populates="population",
        cascade="all, delete-orphan",
    )
    
    characteristics_population = relationship(
        "CharacteristicsPopulation",
        back_populates="population",
        cascade="all, delete-orphan",
    )

    # Datos JSON de la población
    population_json = Column(JSON, nullable=True)


# —————————————————————————————————————————
#  Esquemas Pydantic para Population
# —————————————————————————————————————————
class PopulationBase(BaseModel):
    project_id: int
    population_json: Optional[dict] = None
    
    #Population Affected
    population_type_affected: Optional[str] = "Personas"
    population_number_affected: Optional[int] = None
    population_info_affected: Optional[str] = None
    
    #Population Intervention
    population_type_intervention: Optional[str] = "Personas"
    population_number_intervention: Optional[int] = None
    population_info_intervention: Optional[str] = None

class PopulationCreate(PopulationBase):
    project_id: int
    affected_population: List[AffectedPopulationCreate] = []
    intervention_population: List[InterventionPopulationCreate] = []
    characteristics_population: List[CharacteristicsPopulationCreate] = []

class PopulationResponse(PopulationBase):
    id: int
    affected_population: List[AffectedPopulationResponse] = []
    intervention_population: List[InterventionPopulationResponse] = []
    characteristics_population: List[CharacteristicsPopulationResponse] = []

    class Config:
        from_attributes = True


# —————————————————————————————————————————
#  Rutas de FastAPI para Population
# —————————————————————————————————————————
router = APIRouter()


@router.post("/", response_model=PopulationResponse, status_code=201)
def create_population(payload: PopulationCreate, db: Session = Depends(get_db)):
    # Verificar duplicado de project_id
    exists = db.query(Population).filter_by(project_id=payload.project_id).first()
    if exists:
        raise HTTPException(status_code=400, detail="Population for this project already exists")

    # Crear registro padre
    pop = Population(
        project_id=payload.project_id,
        population_json=payload.population_json,
        population_type_affected=payload.population_type_affected or "Personas",
        population_number_affected=payload.population_number_affected,
        population_info_affected=payload.population_info_affected,
        population_type_intervention=payload.population_type_intervention or "Personas",
        population_number_intervention=payload.population_number_intervention,
        population_info_intervention=payload.population_info_intervention,
    )
    db.add(pop)
    db.flush()  # para obtener pop.id

    # Nota: las filas hijas se gestionan con sus propios endpoints.

    db.commit()
    db.refresh(pop)
    return pop


@router.get("/", response_model=List[PopulationResponse])
def get_all_population(db: Session = Depends(get_db)):
    return db.query(Population).all()


@router.get("/{project_id}", response_model=PopulationResponse)
def get_population_by_project(project_id: int, db: Session = Depends(get_db)):
    pop = db.query(Population).filter(Population.project_id == project_id).first()
    if not pop:
        raise HTTPException(status_code=404, detail="Population not found for this project")
    return pop


@router.put("/{population_id}", response_model=PopulationResponse)
def update_population(population_id: int, payload: PopulationCreate, db: Session = Depends(get_db)):
    pop = db.query(Population).filter(Population.id == population_id).first()
    if not pop:
        raise HTTPException(status_code=404, detail="Population not found")

    # Actualizar campos
    pop.population_json = payload.population_json
    pop.population_type_affected = payload.population_type_affected or "Personas"
    pop.population_number_affected = payload.population_number_affected
    pop.population_info_affected = payload.population_info_affected
    pop.population_type_intervention = payload.population_type_intervention or "Personas"
    pop.population_number_intervention = payload.population_number_intervention
    pop.population_info_intervention = payload.population_info_intervention
    # Si cambia project_id, verificar duplicado
    if pop.project_id != payload.project_id:
        if db.query(Population).filter_by(project_id=payload.project_id).first():
            raise HTTPException(status_code=400, detail="Another population with this project_id exists")
        pop.project_id = payload.project_id

    # Nota: las filas hijas (affected/intervention/characteristics) se gestionan
    # con sus propios endpoints; no se reemplazan aquí.

    db.commit()
    db.refresh(pop)
    return pop


@router.delete("/{population_id}", response_model=dict)
def delete_population(population_id: int, db: Session = Depends(get_db)):
    pop = db.query(Population).filter(Population.id == population_id).first()
    if not pop:
        raise HTTPException(status_code=404, detail="Population not found")
    db.delete(pop)
    db.commit()
    return {"message": "Population deleted"}
