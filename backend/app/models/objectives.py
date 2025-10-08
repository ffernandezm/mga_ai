from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, relationship
from app.core.database import Base, SessionLocal
from sqlalchemy import Column, Integer, Text, ForeignKey
from pydantic import BaseModel
from typing import List

# Modelos relacionados
from app.models.objectives_causes import (
    ObjectivesCauses,
    ObjectivesCausesCreate,
    ObjectivesCausesResponse,
)

from app.models.objectives_indicators import (
    ObjectivesIndicator,
    ObjectivesIndicatorCreate,
    ObjectivesIndicatorResponse,
)

# Conexión DB
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Modelo SQLAlchemy
class Objectives(Base):
    __tablename__ = "objectives"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False, unique=True)
    project = relationship("Project", back_populates="objetives")
    general_problem = Column(Text)
    general_objective = Column(Text)

    objectives_indicators = relationship(
        "ObjectivesIndicator",
        back_populates="objective",
        cascade="all, delete-orphan",
    )

    objectives_causes = relationship(
        "ObjectivesCauses",
        back_populates="objective",
        cascade="all, delete-orphan",
    )

# Esquemas Pydantic
class ObjectivesBase(BaseModel):
    general_problem: str
    general_objective: str


class ObjectivesCreate(ObjectivesBase):
    objectives_causes: List[ObjectivesCausesCreate] = []
    objectives_indicators: List[ObjectivesIndicatorCreate] = []


class ObjectivesUpdate(ObjectivesBase):
    pass


class ObjectivesResponse(ObjectivesBase):
    id: int
    project_id: int
    objectives_causes: List[ObjectivesCausesResponse] = []
    objectives_indicators: List[ObjectivesIndicatorResponse] = []

    class Config:
        from_attributes = True


# Router sin prefijo (se agrega desde main.py)
router = APIRouter()

# Crear un objetivo para un proyecto
@router.post("/{project_id}/", response_model=ObjectivesResponse)
def create_objective(project_id: int, objective: ObjectivesCreate, db: Session = Depends(get_db)):
    db_objective = Objectives(project_id=project_id, **objective.dict())
    db.add(db_objective)
    db.commit()
    db.refresh(db_objective)
    return db_objective


# Listar todos los objetivos de un proyecto
@router.get("/{project_id}/", response_model=List[ObjectivesResponse])
def get_objectives_by_project(project_id: int, db: Session = Depends(get_db)):
    return db.query(Objectives).filter(Objectives.project_id == project_id).all()


# Consultar un objetivo específico
@router.get("/", response_model=List[ObjectivesResponse])
def get_objectives(db: Session = Depends(get_db)):
    return db.query(Objectives).filter().all()


# Actualizar un objetivo
@router.put("/{project_id}/{objective_id}", response_model=ObjectivesResponse)
def update_objective(project_id: int, objective_id: int, objective: ObjectivesUpdate, db: Session = Depends(get_db)):
    db_objective = (
        db.query(Objectives)
        .filter(Objectives.project_id == project_id, Objectives.id == objective_id)
        .first()
    )
    if not db_objective:
        raise HTTPException(status_code=404, detail="Objective not found for this project")

    for key, value in objective.dict(exclude_unset=True).items():
        setattr(db_objective, key, value)

    db.commit()
    db.refresh(db_objective)
    return db_objective


# Eliminar un objetivo
@router.delete("/{project_id}/{objective_id}", response_model=dict)
def delete_objective(project_id: int, objective_id: int, db: Session = Depends(get_db)):
    db_objective = (
        db.query(Objectives)
        .filter(Objectives.project_id == project_id, Objectives.id == objective_id)
        .first()
    )
    if not db_objective:
        raise HTTPException(status_code=404, detail="Objective not found for this project")

    db.delete(db_objective)
    db.commit()
    return {"message": "Objective deleted successfully"}
