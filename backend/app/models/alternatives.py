from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, relationship
from app.core.database import Base, SessionLocal
from sqlalchemy import Column, Integer, Boolean, Text, ForeignKey
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
class Alternatives(Base):
    __tablename__ = "alternatives"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(Text)
    active = Column(Boolean, nullable=False, default=False)
    state = Column(Text)
    
    alternative_id = Column(Integer, ForeignKey("alternatives_general.id"))
    alternative = relationship("AlternativesGeneral", back_populates="alternatives")

# Esquemas Pydantic
class AlternativesBase(BaseModel):
    name: str
    active: bool
    state: str

class AlternativesCreate(AlternativesBase):
    pass

class AlternativesResponse(AlternativesBase):
    id: int

    class Config:
        from_attributes = True  # ✅ equivale a orm_mode

# Rutas de FastAPI
router = APIRouter()

@router.post("/", response_model=AlternativesResponse)
def create_alternative(alternative: AlternativesCreate, db: Session = Depends(get_db)):
    db_alternative = Alternatives(**alternative.dict())
    db.add(db_alternative)
    db.commit()
    db.refresh(db_alternative)
    return db_alternative

@router.get("/", response_model=List[AlternativesResponse])
def get_alternatives(db: Session = Depends(get_db)):
    return db.query(Alternatives).all()

@router.get("/{id}", response_model=AlternativesResponse)
def get_alternative(id: int, db: Session = Depends(get_db)):
    alternative = db.query(Alternatives).filter(Alternatives.id == id).first()
    if not alternative:
        raise HTTPException(status_code=404, detail="Alternative not found")
    return alternative

@router.put("/{id}", response_model=AlternativesResponse)
def update_alternative(id: int, updated: AlternativesCreate, db: Session = Depends(get_db)):
    alternative = db.query(Alternatives).filter(Alternatives.id == id).first()
    if not alternative:
        raise HTTPException(status_code=404, detail="Alternative not found")
    for key, value in updated.dict().items():
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
