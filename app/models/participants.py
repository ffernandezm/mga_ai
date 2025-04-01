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
class Participants(Base):
    __tablename__ = "participants"

    id = Column(Integer, primary_key=True, index=True)
    participant_analysis = Column(Text)

# Esquema Pydantic
class ParticipantsBase(BaseModel):
    participant_analysis: str

class ParticipantsCreate(ParticipantsBase):
    pass

class ParticipantsResponse(ParticipantsBase):
    id: int

    class Config:
        from_attributes  = True

# Rutas de FastAPI
router = APIRouter()

@router.post("/", response_model=ParticipantsResponse)
def create_participant(participant: ParticipantsCreate, db: Session = Depends(get_db)):
    db_participant = Participants(**participant.dict())
    db.add(db_participant)
    db.commit()
    db.refresh(db_participant)
    return db_participant

@router.get("/", response_model=List[ParticipantsResponse])
def get_participants(db: Session = Depends(get_db)):
    return db.query(Participants).all()
