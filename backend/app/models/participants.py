from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import relationship, Session
from app.core.database import Base, SessionLocal
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

FIELD_LABELS = {"participant_actor": "Actor Participante",
                "participant_entity": "Entidad Participante",
                "interest_expectative": "Intereses y Expectativas",
                "rol": "Rol",
                "contribution_conflicts": "Contribuciones y Conflictos"}

# Modelo en SQLAlchemy
class Participants(Base):
    __tablename__ = "participants"
    __table_args__ = {
        "info": {
            "label_plural": "Participantes",
            "label_singular": "Participante",
        }
    }

    id = Column(Integer, primary_key=True)
    participant_actor = Column(Text, info={"label": FIELD_LABELS["participant_actor"]})
    participant_entity = Column(Text, info={"label": FIELD_LABELS["participant_entity"]})
    interest_expectative = Column(Text, info={"label": FIELD_LABELS["interest_expectative"]})
    rol = Column(Text, info={"label": FIELD_LABELS["rol"]})
    contribution_conflicts = Column(Text, info={"label": FIELD_LABELS["contribution_conflicts"]})
    participants_general_id = Column(Integer, ForeignKey("participants_general.id"), nullable=False)

    # Relación declarada, sin importar circularidad porque es por nombre (string)
    participants_general = relationship("ParticipantsGeneral", back_populates="participants")

# Esquema Pydantic
class ParticipantsBase(BaseModel):
    participant_actor: str
    participant_entity: str
    interest_expectative: str
    rol: str
    contribution_conflicts: str

class ParticipantsCreate(ParticipantsBase):
    participants_general_id: int

class ParticipantsResponse(ParticipantsBase):
    id: int
    participants_general_id: int

    model_config = {
        "from_attributes": True
    }

# Rutas de FastAPI
router = APIRouter()

@router.post("/", response_model=ParticipantsResponse)
def create_participant(participant: ParticipantsCreate, db: Session = Depends(get_db)):
    # Importación local para evitar importación circular
    from app.models.participants_general import ParticipantsGeneral

    parent = db.query(ParticipantsGeneral).filter(ParticipantsGeneral.id == participant.participants_general_id).first()
    if not parent:
        raise HTTPException(status_code=400, detail="ParticipantsGeneral with given ID does not exist")

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
    participants = db.query(Participants).join(Participants.participants_general).filter(
        Participants.participants_general.has(project_id=project_id)
    ).all()
    if not participants:
        raise HTTPException(status_code=404, detail="No participants found for this project")
    return participants

@router.delete("/{participant_id}", response_model=dict)
def delete_participant(participant_id: int, db: Session = Depends(get_db)):
    participant = db.query(Participants).filter(Participants.id == participant_id).first()
    if not participant:
        raise HTTPException(status_code=404, detail="Participant not found")
    db.delete(participant)
    db.commit()
    return {"message": "Participant deleted"}

@router.put("/{participant_id}", response_model=ParticipantsResponse)
def update_participant(participant_id: int, updated_data: ParticipantsCreate, db: Session = Depends(get_db)):
    participant = db.query(Participants).filter(Participants.id == participant_id).first()
    if not participant:
        raise HTTPException(status_code=404, detail="Participant not found")

    for key, value in updated_data.dict().items():
        setattr(participant, key, value)

    db.commit()
    db.refresh(participant)
    return participant
