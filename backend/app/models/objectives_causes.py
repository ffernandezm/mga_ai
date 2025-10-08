from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, relationship
from app.core.database import SessionLocal, Base
from sqlalchemy import Column, Integer, Text, ForeignKey
from pydantic import BaseModel
from typing import List


# Conexión a la DB
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Modelo en SQLAlchemy
class ObjectivesCauses(Base):
    __tablename__ = "objectives_causes"

    id = Column(Integer, primary_key=True, index=True)
    type = Column(Text, nullable=True)
    cause_related = Column(Text, nullable=True)
    specifics_objectives = Column(Text, nullable=True)
    
    objective_id = Column(Integer, ForeignKey("objectives.id"))
    objective = relationship("Objectives", back_populates="objectives_causes")

# Esquema Pydantic
class ObjectivesCausesBase(BaseModel):
    type: str
    cause_related: str
    specifics_objectives: str | None = None

class ObjectivesCausesCreate(ObjectivesCausesBase):
    objective_id: int

class ObjectivesCausesUpdate(ObjectivesCausesBase):
    objective_id: int

class ObjectivesCausesResponse(ObjectivesCausesBase):
    id: int
    objective_id: int

    class Config:
        from_attributes = True

# Rutas de FastAPI
router = APIRouter()

# Crear
@router.post("/", response_model=ObjectivesCausesResponse)
def create_objective_causes(objective: ObjectivesCausesCreate, db: Session = Depends(get_db)):
    db_objective = ObjectivesCauses(**objective.dict())
    db.add(db_objective)
    db.commit()
    db.refresh(db_objective)
    return db_objective

# Listar todos
@router.get("/", response_model=List[ObjectivesCausesResponse])
def get_objectives_causes(db: Session = Depends(get_db)):
    return db.query(ObjectivesCauses).all()

# Consultar por ID
@router.get("/{cause_id}", response_model=ObjectivesCausesResponse)
def get_objective_cause_by_id(cause_id: int, db: Session = Depends(get_db)):
    db_objective = db.query(ObjectivesCauses).filter(ObjectivesCauses.id == cause_id).first()
    if not db_objective:
        raise HTTPException(status_code=404, detail="Objective cause not found")
    return db_objective

# Actualizar
@router.put("/{cause_id}", response_model=ObjectivesCausesResponse)
def update_objective_cause(cause_id: int, cause: ObjectivesCausesUpdate, db: Session = Depends(get_db)):
    db_objective = db.query(ObjectivesCauses).filter(ObjectivesCauses.id == cause_id).first()
    if not db_objective:
        raise HTTPException(status_code=404, detail="Objective cause not found")

    for key, value in cause.dict().items():
        setattr(db_objective, key, value)

    db.commit()
    db.refresh(db_objective)
    return db_objective

# Eliminar
@router.delete("/{cause_id}", response_model=dict)
def delete_objective_cause(cause_id: int, db: Session = Depends(get_db)):
    db_objective = db.query(ObjectivesCauses).filter(ObjectivesCauses.id == cause_id).first()
    if not db_objective:
        raise HTTPException(status_code=404, detail="Objective cause not found")

    db.delete(db_objective)
    db.commit()
    return {"message": "Objective cause deleted successfully"}
