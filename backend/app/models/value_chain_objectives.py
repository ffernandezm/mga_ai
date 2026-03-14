from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, relationship
from sqlalchemy import Column, Integer, String, ForeignKey
from pydantic import BaseModel
from typing import List, Optional

from app.core.database import Base, SessionLocal

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Modelo en SQLAlchemy
class ValueChainObjectives(Base):
    __tablename__ = "value_chain_objectives"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    value_chain_id = Column(Integer, ForeignKey("value_chains.id"), nullable=False)
    name = Column(String, index=True)  # Assuming a name field, adjust if needed

    # Relación con Project
    project = relationship("Project", back_populates="value_chain_objectives")

    # Relación con ValueChain
    value_chain = relationship("ValueChain", back_populates="value_chain_objectives")

    # Relación con Products
    products = relationship(
        "Product",
        back_populates="value_chain_objective",
        cascade="all, delete-orphan"
    )

    # Relación con ObjectivesCauses
    objectives_causes = relationship(
        "ObjectivesCauses",
        back_populates="value_chain_objective",
        cascade="all, delete-orphan"
    )

# Esquema Pydantic
class ValueChainObjectivesBase(BaseModel):
    project_id: int
    value_chain_id: int
    name: Optional[str] = None

class ValueChainObjectivesCreate(BaseModel):
    project_id: int
    value_chain_id: int
    name: Optional[str] = None

class ValueChainObjectivesResponse(ValueChainObjectivesBase):
    id: int

    class Config:
        from_attributes = True

# Rutas de FastAPI
router = APIRouter()

# Obtener todos los value chain objectives
@router.get("/", response_model=List[ValueChainObjectivesResponse])
def get_value_chain_objectives(db: Session = Depends(get_db)):
    objectives = db.query(ValueChainObjectives).all()
    return objectives

# Obtener un value chain objective por ID
@router.get("/{objective_id}", response_model=ValueChainObjectivesResponse)
def get_value_chain_objective(objective_id: int, db: Session = Depends(get_db)):
    objective = db.query(ValueChainObjectives).filter(ValueChainObjectives.id == objective_id).first()
    if not objective:
        raise HTTPException(status_code=404, detail="Value Chain Objective not found")
    return objective

# Crear un nuevo value chain objective
@router.post("/", response_model=ValueChainObjectivesResponse, status_code=201)
def create_value_chain_objective(objective: ValueChainObjectivesCreate, db: Session = Depends(get_db)):
    new_objective = ValueChainObjectives(**objective.model_dump())
    db.add(new_objective)
    db.commit()
    db.refresh(new_objective)
    return new_objective

# Actualizar un value chain objective
@router.put("/{objective_id}", response_model=ValueChainObjectivesResponse)
def update_value_chain_objective(objective_id: int, objective: ValueChainObjectivesCreate, db: Session = Depends(get_db)):
    db_objective = db.query(ValueChainObjectives).filter(ValueChainObjectives.id == objective_id).first()
    if not db_objective:
        raise HTTPException(status_code=404, detail="Value Chain Objective not found")
    for key, value in objective.model_dump().items():
        setattr(db_objective, key, value)
    db.commit()
    db.refresh(db_objective)
    return db_objective

# Eliminar un value chain objective
@router.delete("/{objective_id}")
def delete_value_chain_objective(objective_id: int, db: Session = Depends(get_db)):
    db_objective = db.query(ValueChainObjectives).filter(ValueChainObjectives.id == objective_id).first()
    if not db_objective:
        raise HTTPException(status_code=404, detail="Value Chain Objective not found")
    db.delete(db_objective)
    db.commit()
    return {"message": "Value Chain Objective deleted successfully"}