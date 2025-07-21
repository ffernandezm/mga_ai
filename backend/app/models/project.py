from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, relationship
from sqlalchemy import Column, Integer, String, ForeignKey
from pydantic import BaseModel
from typing import List, Optional

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
    __table_args__ = {"extend_existing": True}

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    description = Column(String)
    problem_id = Column(Integer, ForeignKey("problems.id"), nullable=True)
    participants_general_id = Column(Integer, ForeignKey("participants_general.id"), nullable=True)


    problem = relationship("Problem", back_populates="projects")

    # Relación opcional con ParticipantsGeneral
    participants_general = relationship(
        "ParticipantsGeneral",
        foreign_keys=[participants_general_id]
    )


# Esquema Pydantic
class ProjectBase(BaseModel):
    name: str
    description: str
    problem_id: Optional[int] = None  # Campo opcional
    participants_general_id: Optional[int] = None  # Campo opcional

class ProjectCreate(BaseModel):
    name: str
    description: Optional[str] = None
    problem_id: Optional[int] = None
    participants_general_id: Optional[int] = None

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
@router.post("/", response_model=ProjectResponse)
def create_project(project: ProjectCreate, db: Session = Depends(get_db)):
    new_project = Project(**project.model_dump())
    db.add(new_project)  
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


