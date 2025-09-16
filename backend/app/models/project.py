from fastapi import APIRouter, Depends, HTTPException
import csv
import os
from sqlalchemy.orm import Session, relationship
from sqlalchemy import Column, Integer, String, ForeignKey
from pydantic import BaseModel
from typing import List, Optional

from app.models.participants_general import ParticipantsGeneral
from app.models.population import Population
from app.models.characteristics_population import CharacteristicsPopulation

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

    # Relación con Problem (CORREGIDO)
    problem = relationship(
        "Problem",
        back_populates="project",
        uselist=False,
        cascade="all, delete-orphan"
    )

    # Relación con ParticipantsGeneral
    participants_general = relationship(
        "ParticipantsGeneral",
        back_populates="project",
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

# Esquema Pydantic
class ProjectBase(BaseModel):
    name: str
    description: Optional[str] = None

class ProjectCreate(BaseModel):
    name: str
    description: Optional[str] = None

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
    from app.models.problem import Problem
    # 1. Crear el proyecto
    new_project = Project(**project.model_dump())
    db.add(new_project)
    db.flush()

    # 2. Crear automáticamente un registro en Problem
    problem = Problem(
        project_id=new_project.id
    )
    
    # 2. Crear automáticamente un registro en ParticipantsGeneral asociado
    participants_general = ParticipantsGeneral(
        participants_analisis="",
        project_id=new_project.id
    )

    # 3. Crear automáticamente un registro en Population asociado
    population = Population(
        project_id=new_project.id
    )
    db.add_all([problem, participants_general, population])
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

    for key, value in updated_data.model_dump().items():
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


