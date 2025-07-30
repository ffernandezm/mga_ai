from fastapi import APIRouter, Depends, HTTPException, Body, Query

from sqlalchemy.orm import relationship
from sqlalchemy import Column, Integer, Text, ForeignKey, JSON
from pydantic import BaseModel
from sqlalchemy.orm import Session, relationship
from app.core.database import Base, SessionLocal
from typing import List, Optional


from app.models.participants import ParticipantsResponse, ParticipantsCreate, Participants

from app.ai.main import main
# Conexión a la DB
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Modelo en SQLAlchemy
class ParticipantsGeneral(Base):
    __tablename__ = "participants_general"

    id = Column(Integer, primary_key=True, index=True)
    participants_analisis = Column(Text)
    
    # Relación obligatoria a un proyecto
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False, unique=True)
    project = relationship("Project", back_populates="participants_general")
    
    # Relación con tabla Participants
    participants = relationship("Participants", back_populates="participants_general")
    
    # Campo Json que será usado para promt al LLM
    participants_json = Column(JSON, nullable=True)

# Esquema Pydantic
class ParticipantsGeneralBase(BaseModel):
    participants_analisis: str
    
    participants_json: Optional[dict] = None  # Acepta un diccionario como JSON


class ParticipantsGeneralCreate(ParticipantsGeneralBase):
    project_id: int
    participants: List[ParticipantsCreate] = []
    

class ParticipantsGeneralResponse(ParticipantsGeneralBase):
    id: int
    
    participants: List[ParticipantsResponse] = []

    class Config:
        from_attributes  = True
        

# Rutas de FastAPI
router = APIRouter()


@router.post("/", response_model=ParticipantsGeneralResponse)
def create_participant_general(participant: ParticipantsGeneralCreate, db: Session = Depends(get_db)):
    db_participant_general = ParticipantsGeneral(
        participants_analisis=participant.participants_analisis,
        project_id=participant.project_id
    )
    
    db.add(db_participant_general)
    db.flush()  # Asegura tener el ID antes de crear los hijos

    # Crear cada participant hijo
    for p in participant.participants:
        db_participant = Participants(
            participant_actor=p.participant_actor,
            participant_entity=p.participant_entity,
            interest_expectative=p.interest_expectative,
            rol=p.rol,
            contribution_conflicts=p.contribution_conflicts,
            participants_general_id=db_participant_general.id
        )
        db.add(db_participant)

    db.commit()
    db.refresh(db_participant_general)
    return db_participant_general


@router.get("/", response_model=List[ParticipantsResponse])
def get_participants_general(db: Session = Depends(get_db)):
    return db.query(ParticipantsGeneral).all()

@router.get("/{project_id}", response_model=List[ParticipantsGeneralResponse])
def get_project_participants_general(project_id: int, db: Session = Depends(get_db)):
    return db.query(ParticipantsGeneral).filter(ParticipantsGeneral.project_id == project_id).all()


@router.delete("/{participant_id}", response_model=dict)
def delete_participant_general(participant_id: int, db: Session = Depends(get_db)):
    participant = db.query(ParticipantsGeneral).filter(ParticipantsGeneral.id == participant_id).first()
    if not participant:
        raise HTTPException(status_code=404, detail="Participant not found")
    db.delete(participant)
    db.commit()
    return {"message": "Participant deleted"}

@router.put("/{participant_id}", response_model=ParticipantsGeneralResponse)
def update_participant_general(participant_id: int, updated_data: ParticipantsGeneralCreate, db: Session = Depends(get_db)):
    participant = db.query(ParticipantsGeneral).filter(ParticipantsGeneral.id == participant_id).first()
    if not participant:
        raise HTTPException(status_code=404, detail="Participant not found")

    for key, value in updated_data.dict(exclude={"participants"}, exclude_unset=True).items():
        setattr(participant, key, value)

    db.commit()
    db.refresh(participant)
    return participant
