from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, relationship
from app.core.database import SessionLocal, Base
from sqlalchemy import Column, Integer, Text, ForeignKey
from pydantic import BaseModel
from typing import List

# Importar modelos relacionados
from app.models.value_chain_objectives import ValueChainObjectives
from app.models.value_chain import ValueChain


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
    cause_id = Column(Integer, nullable=True)  # ID de la causa (directa o indirecta)
    value_chain_objective_id = Column(Integer, ForeignKey("value_chain_objectives.id"), nullable=True)  # Relación con ValueChainObjectives
    
    objective_id = Column(Integer, ForeignKey("objectives.id"))
    objective = relationship("Objectives", back_populates="objectives_causes")
    
    # Relación con ValueChainObjectives
    value_chain_objective = relationship("ValueChainObjectives", back_populates="objectives_causes")

# Esquema Pydantic
class ObjectivesCausesBase(BaseModel):
    type: str
    cause_related: str
    specifics_objectives: str | None = None
    cause_id: int | None = None
    value_chain_objective_id: int | None = None

class ObjectivesCausesCreate(ObjectivesCausesBase):
    objective_id: int

class ObjectivesCausesUpdate(BaseModel):
    type: str
    cause_related: str
    specifics_objectives: str | None = None
    cause_id: int | None = None
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
    from app.models.objectives import Objectives
    
    db_objective = ObjectivesCauses(**objective.dict())
    db.add(db_objective)
    db.commit()
    db.refresh(db_objective)
    
    # Sincronizar con ValueChainObjectives si es causa directa
    if objective.type.lower() == "directa" and objective.specifics_objectives:
        # Obtener project_id desde objective_id
        obj = db.query(Objectives).filter(Objectives.id == objective.objective_id).first()
        if obj:
            # Obtener value_chain_id del proyecto (asumiendo una por proyecto)
            value_chain = db.query(ValueChain).filter(ValueChain.project_id == obj.project_id).first()
            if value_chain:
                # Crear ValueChainObjectives
                vc_obj = ValueChainObjectives(
                    project_id=obj.project_id,
                    value_chain_id=value_chain.id,
                    name=objective.specifics_objectives
                )
                db.add(vc_obj)
                db.commit()
                db.refresh(vc_obj)
                # Actualizar el campo value_chain_objective_id
                db_objective.value_chain_objective_id = vc_obj.id
                db.commit()
    
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
    from app.models.objectives import Objectives
    
    db_objective = db.query(ObjectivesCauses).filter(ObjectivesCauses.id == cause_id).first()
    if not db_objective:
        raise HTTPException(status_code=404, detail="Objective cause not found")

    old_type = db_objective.type
    old_specifics = db_objective.specifics_objectives

    for key, value in cause.dict().items():
        setattr(db_objective, key, value)

    db.commit()
    db.refresh(db_objective)

    # Sincronizar con ValueChainObjectives
    if cause.type.lower() == "directa" and cause.specifics_objectives:
        if db_objective.value_chain_objective_id:
            # Actualizar existente
            vc_obj = db.query(ValueChainObjectives).filter(ValueChainObjectives.id == db_objective.value_chain_objective_id).first()
            if vc_obj:
                vc_obj.name = cause.specifics_objectives
                db.commit()
        else:
            # Crear nuevo si no existe
            obj = db.query(Objectives).filter(Objectives.id == cause.objective_id).first()
            if obj:
                value_chain = db.query(ValueChain).filter(ValueChain.project_id == obj.project_id).first()
                if value_chain:
                    vc_obj = ValueChainObjectives(
                        project_id=obj.project_id,
                        value_chain_id=value_chain.id,
                        name=cause.specifics_objectives
                    )
                    db.add(vc_obj)
                    db.commit()
                    db.refresh(vc_obj)
                    db_objective.value_chain_objective_id = vc_obj.id
                    db.commit()
    elif old_type and old_type.lower() == "directa" and cause.type.lower() != "directa":
        # Cambió de directa a no directa, eliminar
        if db_objective.value_chain_objective_id:
            vc_obj = db.query(ValueChainObjectives).filter(ValueChainObjectives.id == db_objective.value_chain_objective_id).first()
            if vc_obj:
                db.delete(vc_obj)
                db.commit()
            db_objective.value_chain_objective_id = None
            db.commit()

    return db_objective

# Eliminar
@router.delete("/{cause_id}", response_model=dict)
def delete_objective_cause(cause_id: int, db: Session = Depends(get_db)):
    db_objective = db.query(ObjectivesCauses).filter(ObjectivesCauses.id == cause_id).first()
    if not db_objective:
        raise HTTPException(status_code=404, detail="Objective cause not found")

    # Si es directa, eliminar el correspondiente ValueChainObjectives
    if db_objective.type and db_objective.type.lower() == "directa" and db_objective.value_chain_objective_id:
        vc_obj = db.query(ValueChainObjectives).filter(ValueChainObjectives.id == db_objective.value_chain_objective_id).first()
        if vc_obj:
            db.delete(vc_obj)

    db.delete(db_objective)
    db.commit()
    return {"message": "Objective cause deleted successfully"}
