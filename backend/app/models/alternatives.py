from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, relationship
from app.core.database import Base, SessionLocal
from sqlalchemy import Column, Integer, Boolean, Text, ForeignKey
from pydantic import BaseModel
from typing import List, Optional

# Conexión a la DB
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Modelo en SQLAlchemy
class Alternatives(Base):
    __tablename__ = "alternatives"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(Text)
    active = Column(Boolean, nullable=False, default=False)
    state = Column(Text)
    
    alternative_id = Column(Integer, ForeignKey("alternatives_general.id"), nullable=False)
    alternative = relationship("AlternativesGeneral", back_populates="alternatives")

# Esquemas Pydantic
class AlternativesBase(BaseModel):
    name: str
    active: bool
    state: str

class AlternativesCreate(AlternativesBase):
    alternative_id: Optional[int] = None
    project_id: Optional[int] = None


class AlternativesNestedCreate(AlternativesBase):
    pass


class AlternativesUpdate(BaseModel):
    name: Optional[str] = None
    active: Optional[bool] = None
    state: Optional[str] = None
    alternative_id: Optional[int] = None
    project_id: Optional[int] = None

class AlternativesResponse(AlternativesBase):
    id: int
    alternative_id: int

    class Config:
        from_attributes = True  # ✅ equivale a orm_mode

# Rutas de FastAPI
router = APIRouter()

@router.post("/", response_model=AlternativesResponse)
def create_alternative(alternative: AlternativesCreate, db: Session = Depends(get_db)):
    # Importación local para evitar importación circular
    from app.models.alternatives_general import AlternativesGeneral

    parent = None
    if alternative.alternative_id is not None:
        parent = db.query(AlternativesGeneral).filter(
            AlternativesGeneral.id == alternative.alternative_id
        ).first()
    elif alternative.project_id is not None:
        parent = db.query(AlternativesGeneral).filter(
            AlternativesGeneral.project_id == alternative.project_id
        ).first()
    else:
        raise HTTPException(status_code=422, detail="Debe enviar 'alternative_id' o 'project_id'")

    if not parent:
        raise HTTPException(status_code=400, detail="AlternativesGeneral no existe para el identificador enviado")

    db_alternative = Alternatives(
        name=alternative.name,
        active=alternative.active,
        state=alternative.state,
        alternative_id=parent.id,
    )
    db.add(db_alternative)
    db.commit()
    db.refresh(db_alternative)
    return db_alternative

@router.get("/", response_model=List[AlternativesResponse])
def get_alternatives(db: Session = Depends(get_db)):
    return db.query(Alternatives).all()

@router.get("/project/{project_id}", response_model=List[AlternativesResponse])
def get_project_alternatives(project_id: int, db: Session = Depends(get_db)):
    alternatives = db.query(Alternatives).join(Alternatives.alternative).filter(
        Alternatives.alternative.has(project_id=project_id)
    ).all()
    if not alternatives:
        raise HTTPException(status_code=404, detail="No alternatives found for this project")
    return alternatives

@router.get("/{id}", response_model=AlternativesResponse)
def get_alternative(id: int, db: Session = Depends(get_db)):
    alternative = db.query(Alternatives).filter(Alternatives.id == id).first()
    if not alternative:
        raise HTTPException(status_code=404, detail="Alternative not found")
    return alternative

@router.put("/{id}", response_model=AlternativesResponse)
def update_alternative(id: int, updated: AlternativesUpdate, db: Session = Depends(get_db)):
    alternative = db.query(Alternatives).filter(Alternatives.id == id).first()
    if not alternative:
        raise HTTPException(status_code=404, detail="Alternative not found")

    from app.models.alternatives_general import AlternativesGeneral

    new_parent_id = None
    if updated.alternative_id is not None:
        new_parent_id = updated.alternative_id
    elif updated.project_id is not None:
        parent = db.query(AlternativesGeneral).filter(
            AlternativesGeneral.project_id == updated.project_id
        ).first()
        if not parent:
            raise HTTPException(status_code=400, detail="AlternativesGeneral no existe para el project_id enviado")
        new_parent_id = parent.id

    if new_parent_id is not None:
        parent_exists = db.query(AlternativesGeneral).filter(
            AlternativesGeneral.id == new_parent_id
        ).first()
        if not parent_exists:
            raise HTTPException(status_code=400, detail="AlternativesGeneral with given ID does not exist")
        alternative.alternative_id = new_parent_id

    update_data = updated.model_dump(exclude_unset=True, exclude={"alternative_id", "project_id"})
    for key, value in update_data.items():
        setattr(alternative, key, value)

    db.commit()
    db.refresh(alternative)
    return alternative

@router.delete("/{id}")
def delete_alternative(id: int, db: Session = Depends(get_db)):
    alternative = db.query(Alternatives).filter(Alternatives.id == id).first()
    if not alternative:
        raise HTTPException(status_code=404, detail="Alternative not found")
    db.delete(alternative)
    db.commit()
    return {"message": "Alternative deleted successfully"}
