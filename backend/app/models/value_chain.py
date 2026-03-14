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
class ValueChain(Base):
    __tablename__ = "value_chains"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    name = Column(String, index=True)  # Assuming a name field, adjust if needed

    # Relación con Project
    project = relationship("Project", back_populates="value_chains")

    # Relación con ValueChainObjectives
    value_chain_objectives = relationship(
        "ValueChainObjectives",
        back_populates="value_chain",
        cascade="all, delete-orphan"
    )

# Esquema Pydantic
class ValueChainBase(BaseModel):
    project_id: int
    name: Optional[str] = None

class ValueChainCreate(BaseModel):
    project_id: int
    name: Optional[str] = None

class ValueChainResponse(ValueChainBase):
    id: int

    class Config:
        from_attributes = True

# Rutas de FastAPI
router = APIRouter()

# Obtener todos los value chains
@router.get("/", response_model=List[ValueChainResponse])
def get_value_chains(db: Session = Depends(get_db)):
    value_chains = db.query(ValueChain).all()
    return value_chains

# Obtener un value chain por ID
@router.get("/{value_chain_id}", response_model=ValueChainResponse)
def get_value_chain(value_chain_id: int, db: Session = Depends(get_db)):
    value_chain = db.query(ValueChain).filter(ValueChain.id == value_chain_id).first()
    if not value_chain:
        raise HTTPException(status_code=404, detail="Value Chain not found")
    return value_chain

# Crear un nuevo value chain
@router.post("/", response_model=ValueChainResponse, status_code=201)
def create_value_chain(value_chain: ValueChainCreate, db: Session = Depends(get_db)):
    new_value_chain = ValueChain(**value_chain.model_dump())
    db.add(new_value_chain)
    db.commit()
    db.refresh(new_value_chain)
    return new_value_chain

# Actualizar un value chain
@router.put("/{value_chain_id}", response_model=ValueChainResponse)
def update_value_chain(value_chain_id: int, value_chain: ValueChainCreate, db: Session = Depends(get_db)):
    db_value_chain = db.query(ValueChain).filter(ValueChain.id == value_chain_id).first()
    if not db_value_chain:
        raise HTTPException(status_code=404, detail="Value Chain not found")
    for key, value in value_chain.model_dump().items():
        setattr(db_value_chain, key, value)
    db.commit()
    db.refresh(db_value_chain)
    return db_value_chain

# Eliminar un value chain
@router.delete("/{value_chain_id}")
def delete_value_chain(value_chain_id: int, db: Session = Depends(get_db)):
    db_value_chain = db.query(ValueChain).filter(ValueChain.id == value_chain_id).first()
    if not db_value_chain:
        raise HTTPException(status_code=404, detail="Value Chain not found")
    db.delete(db_value_chain)
    db.commit()
    return {"message": "Value Chain deleted successfully"}