from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import relationship
from sqlalchemy.orm import Session
from app.core.database import Base, SessionLocal
from sqlalchemy import Column, Integer, Text, ForeignKey
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
class Participants(Base):
    __tablename__ = "participants"

    id = Column(Integer, primary_key=True, index=True)
    participant_analysis = Column(Text)
    interest_expectative = Column(Text)
    rol = Column(Text)
    contribution_conflicts = Column(Text)
    project_id = Column(Integer, ForeignKey("projects.id"))
    
    projects = relationship("Project", back_populates="participants")
    
# Esquema Pydantic
class ParticipantsBase(BaseModel):
    participant_analysis: str
    interest_expectative: str
    rol: str
    contribution_conflicts: str
    project_id: Optional[int] = None  # Nuevo campo opcional

class ParticipantsCreate(ParticipantsBase):
    project_id: int

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

@router.get("/{project_id}", response_model=List[ParticipantsResponse])
def get_project_participants(project_id: int, db: Session = Depends(get_db)):
    participants = db.query(Participants).filter(Participants.project_id == project_id).all()
    if not participants:
        raise HTTPException(status_code=404, detail="No participants found for this project")

    return participants