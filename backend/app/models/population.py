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

# —————————————————————————————————————————
#  Modelo SQLAlchemy: Population
# —————————————————————————————————————————
class Population(Base):
    __tablename__ = "population"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False, unique=True)

    # Relaciones
    project = relationship("Project", back_populates="population")
    
    population_type_affected = Column(Text, nullable=True)
    number_affected = Column(Integer, nullable=True)
    source_information_affected = Column(Text, nullable=True)
    affected_population = relationship(
        "AffectedPopulation",
        back_populates="population",
        cascade="all, delete-orphan",
    )
    
    population_type_intervention = Column(Text, nullable=False, default="No especificado")
    number_intervention = Column(Integer, nullable=False, default=0)
    source_information_intervention = Column(Text, nullable=True)
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
    population_type_affected: Optional[str] = None
    number_affected: Optional[int] = None
    source_information_affected: Optional[str] = None
    
    #Population Intervention
    population_type_intervention: Optional[str] = None
    number_intervention: Optional[int] = None
    source_information_intervention: Optional[str] = None

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
    )
    db.add(pop)
    db.flush()  # para obtener pop.id

    # Crear hijos
    for group in payload.affected_population:
        child = AffectedPopulation(
            population_id=pop.id,
            population_type=group.population_type,
            number=group.number,
            source_information=group.source_information,
        )
        db.add(child)
    
    # for group in payload.affected_population:
    #     child = AffectedPopulation(
    #         population_id=pop.id,
    #         population_type=group.population_type,
    #         number=group.number,
    #         source_information=group.source_information,
    #     )
    #     db.add(child)

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


@router.put("/{project_id}", response_model=PopulationResponse)
def update_population(population_id: int, payload: PopulationCreate, db: Session = Depends(get_db)):
    pop = db.query(Population).filter(Population.id == population_id).first()
    if not pop:
        raise HTTPException(status_code=404, detail="Population not found")

    # Actualizar campos
    pop.population_json = payload.population_json
    # Si cambia project_id, verificar duplicado
    if pop.project_id != payload.project_id:
        if db.query(Population).filter_by(project_id=payload.project_id).first():
            raise HTTPException(status_code=400, detail="Another population with this project_id exists")
        pop.project_id = payload.project_id

    # Reemplazar hijos: borra y vuelve a crear
    pop.affected_population.clear()
    for group in payload.affected_population:
        child = AffectedPopulation(
            population_id=pop.id,
            population_type=group.population_type,
            number=group.number,
            source_information=group.source_information,
        )
        db.add(child)

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
