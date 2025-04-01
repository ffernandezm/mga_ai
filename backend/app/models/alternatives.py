from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import Base, SessionLocal
from sqlalchemy import Column, Integer, Text
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
    solution_alternatives = Column(Text)

# Esquema Pydantic
class AlternativesBase(BaseModel):
    solution_alternatives: str

class AlternativesCreate(AlternativesBase):
    pass

class AlternativesResponse(AlternativesBase):
    id: int

    class Config:
        from_attributes  = True

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
