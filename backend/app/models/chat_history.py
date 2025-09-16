from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime, select
from sqlalchemy.orm import relationship, Session

from datetime import datetime
from app.core.database import Base, SessionLocal
from pydantic import BaseModel
from typing import List
from sqlalchemy.sql import func

from fastapi import APIRouter, Depends, HTTPException

class ChatHistory(Base):
    __tablename__ = "chat_history"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    tab = Column(String, nullable=False)   # Ej: "problems", "participants", etc.
    sender = Column(String, nullable=False)  # "user" o "bot"
    message = Column(Text, nullable=False)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())


# ----------------- Esquemas Pydantic -----------------
class ChatMessageBase(BaseModel):
    project_id: int
    tab: str
    sender: str
    message: str


class ChatMessageCreate(ChatMessageBase):
    pass


class ChatMessageResponse(ChatMessageBase):
    id: int
    timestamp: datetime

    class Config:
        from_attributes = True


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/chat/{project_id}/{tab}", response_model=List[ChatMessageResponse])
def get_chat_history(project_id: int, tab: str, db: Session = Depends(get_db)):
    """
    Devuelve el historial de chat como lista de mensajes individuales
    """
    messages = (
        db.query(ChatHistory)
        .filter(ChatHistory.project_id == project_id, ChatHistory.tab == tab)
        .order_by(ChatHistory.timestamp.asc())
        .all()
    )

    return messages

@router.delete("/chat/{project_id}/{tab}")
def clear_chat_history(project_id: int, tab: str, db: Session = Depends(get_db)):
    """
    Elimina todos los mensajes del historial de chat para un proyecto y tab específicos.
    """
    deleted = (
        db.query(ChatHistory)
        .filter(ChatHistory.project_id == project_id, ChatHistory.tab == tab)
        .delete()
    )
    db.commit()

    if deleted == 0:
        raise HTTPException(status_code=404, detail="No se encontraron mensajes para eliminar")

    return {"message": f"Se eliminaron {deleted} mensajes del chat"}
