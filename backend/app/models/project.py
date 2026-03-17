from fastapi import APIRouter, Depends, HTTPException
import csv
import os
from sqlalchemy.orm import Session, relationship
from sqlalchemy import Column, Integer, String, ForeignKey
from pydantic import BaseModel
from typing import List, Optional

from app.models.problems import Problems
from app.models.participants_general import ParticipantsGeneral
from app.models.population import Population
from app.models.characteristics_population import CharacteristicsPopulation
from app.models.objectives import Objectives
from app.models.alternatives_general import AlternativesGeneral
from app.models.requirements_general import RequirementsGeneral
from app.models.technical_analysis import TechnicalAnalysis
from app.models.localization_general import LocalizationGeneral
from app.models.value_chain import ValueChain
from app.models.development_plans import DevelopmentPlans
# Conexión a la DB
from app.core.database import Base, SessionLocal

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Modelo en SQLAlchemy
class Project(Base):
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    description = Column(String)
    process = Column(String)
    object_desc = Column(String) # 'objeto' es palabra reservada en algunos contextos, uso object_desc
    region = Column(String)
    department = Column(String)
    municipality = Column(String)
    intervention_type = Column(String)
    project_typology = Column(String)
    main_product = Column(String)
    sector = Column(String)

    # Relación con Problems (CORREGIDO)
    problem = relationship(
        "Problems",
        back_populates="project",
        uselist=False,
        cascade="all, delete-orphan"
    )

    # Relación con ParticipantsGeneral
    participants_general = relationship(
        "ParticipantsGeneral",
        back_populates="project",
        cascade="all, delete-orphan",
        uselist=False,
        foreign_keys="ParticipantsGeneral.project_id"
    )

    # Relación con Population
    population = relationship(
        "Population",
        uselist=False,
        back_populates="project",
        cascade="all, delete-orphan"
    )
    
    objetives = relationship(
        "Objectives",
        uselist=False,
        back_populates="project",
        cascade="all, delete-orphan"
    )
    
    alternatives_general = relationship(
        "AlternativesGeneral",
        uselist=False,
        back_populates="project",
        cascade="all, delete-orphan"
    )

    requirements_general = relationship(
        "RequirementsGeneral",
        uselist=False,
        back_populates="project",
        cascade="all, delete-orphan"
    )

    technical_analysis = relationship(
        "TechnicalAnalysis",
        uselist=False,
        back_populates="project",
        cascade="all, delete-orphan"
    )

    localization_general = relationship(
        "LocalizationGeneral",
        uselist=False,
        back_populates="project",
        cascade="all, delete-orphan"
    )
    
    survey = relationship(
        "Survey",
        uselist=False,
        back_populates="project",
        cascade="all, delete-orphan"
    )

    # Relación con ValueChains
    value_chains = relationship(
        "ValueChain",
        back_populates="project",
        cascade="all, delete-orphan"
    )

    # Relación con ValueChainObjectives
    value_chain_objectives = relationship(
        "ValueChainObjectives",
        back_populates="project",
        cascade="all, delete-orphan"
    )

    # Relación con Products
    products = relationship(
        "Product",
        back_populates="project",
        cascade="all, delete-orphan"
    )

    # Relación con Activities
    activities = relationship(
        "Activity",
        back_populates="project",
        cascade="all, delete-orphan"
    )

    # Relación con DevelopmentPlan
    development_plan = relationship(
        "DevelopmentPlans",
        uselist=False,
        back_populates="project",
        cascade="all, delete-orphan"
    )



# Esquema Pydantic
class ProjectBase(BaseModel):
    name: str
    description: Optional[str] = None
    process: Optional[str] = ""
    object_desc: Optional[str] = ""
    region: Optional[str] = ""
    department: Optional[str] = ""
    municipality: Optional[str] = ""
    intervention_type: Optional[str] = ""
    project_typology: Optional[str] = ""
    main_product: Optional[str] = ""
    sector: Optional[str] = ""

class ProjectCreate(BaseModel):
    name: str
    description: Optional[str] = None
    process: Optional[str] = ""
    object_desc: Optional[str] = ""
    region: Optional[str] = ""
    department: Optional[str] = ""
    municipality: Optional[str] = ""
    intervention_type: Optional[str] = ""
    project_typology: Optional[str] = ""
    main_product: Optional[str] = ""
    sector: Optional[str] = ""

class ProjectUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    process: Optional[str] = None
    object_desc: Optional[str] = None
    region: Optional[str] = None
    department: Optional[str] = None
    municipality: Optional[str] = None
    intervention_type: Optional[str] = None
    project_typology: Optional[str] = None
    main_product: Optional[str] = None
    sector: Optional[str] = None

class ProjectResponse(ProjectBase):
    id: int

    class Config:
        from_attributes = True

# Rutas de FastAPI
router = APIRouter()

# Obtener todos los proyectos
@router.get("/", response_model=List[ProjectResponse])
def get_projects(db: Session = Depends(get_db)):
    projects = db.query(Project).all()
    return projects

# Obtener un proyecto por ID
@router.get("/{project_id}", response_model=ProjectResponse)
def get_project(project_id: int, db: Session = Depends(get_db)):
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project

# Crear un nuevo proyecto
@router.post("/", response_model=ProjectResponse, status_code=201)
def create_project(project: ProjectCreate, db: Session = Depends(get_db)):
    from app.models.problems import Problems
    # 1. Crear el proyecto
    new_project = Project(**project.model_dump())
    db.add(new_project)
    db.flush()

    # Crear plan de desarrollo

    development_plan = DevelopmentPlans(project_id=new_project.id)

    #Crear automáticamente un registro en Problems
    problem = Problems(
        project_id=new_project.id,
        central_problem= "",
        current_description= "",
        magnitude_problem="",
        direct_effects= [],
        direct_causes= [],
    )
    
    # Crear automáticamente un registro en ParticipantsGeneral asociado
    participants_general = ParticipantsGeneral(
        participants_analisis="",
        project_id=new_project.id
    )

    # Crear automáticamente un registro en Population asociado
    population = Population(
        project_id=new_project.id
    )
    
    # Crear automáticamente un registro en Objectives asociado
    objectives = Objectives(
        project_id=new_project.id
    )
    
    # Crear automáticamente un registro en AlternativesGeneral asociado
    alternatives_general = AlternativesGeneral(
        project_id=new_project.id
    )

    # Crear automáticamente un registro en RequirementsGeneral asociado
    requirements_general = RequirementsGeneral(
        project_id=new_project.id
    )

    # Crear automáticamente un registro en TechnicalAnalysis asociado
    technical_analysis = TechnicalAnalysis(
        project_id=new_project.id
    )
    
    # Crear automáticamente un registro en LocalizationGeneral asociado
    localization_general = LocalizationGeneral(
        project_id=new_project.id
    )

    # Crear automáticamente un registro en ValueChain asociado
    value_chains = ValueChain(
        project_id=new_project.id,
    )

    db.add_all([
                development_plan,
                problem,
                participants_general,
                population,
                objectives,
                alternatives_general,
                requirements_general,
                technical_analysis,
                localization_general,
                value_chains
                ])
    db.flush()  # para obtener population.id antes de usarlo

    # 4. Cargar los datos predeterminados desde el CSV
    csv_path = os.path.join(os.path.dirname(__file__), "..", "data", "characteristics_population.csv")
    with open(csv_path, newline="", encoding="utf-8") as csvfile:
        reader = csv.DictReader(csvfile)
        default_records = [
            CharacteristicsPopulation(
                classification=row["classification"],
                detail=row["detail"],
                people_number=int(row["people_number"]),
                information=row["information"],
                population_id=population.id
            )
            for row in reader
        ]

    db.add_all(default_records)

    # 5. Commit y refrescar
    db.commit()
    db.refresh(new_project)
    return new_project

# Actualizar un proyecto por ID
@router.put("/{project_id}", response_model=ProjectResponse)
def update_project(project_id: int, updated_data: ProjectCreate, db: Session = Depends(get_db)):
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    for key, value in updated_data.model_dump(exclude_unset=True).items():
        setattr(project, key, value)

    db.commit()
    db.refresh(project)
    return project

# Eliminar un proyecto
@router.delete("/{project_id}", response_model=dict)
def delete_project(project_id: int, db: Session = Depends(get_db)):
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    db.delete(project)
    db.commit()
    return {"message": "Project deleted successfully"}


