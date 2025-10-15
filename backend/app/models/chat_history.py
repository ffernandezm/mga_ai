# app/models/chat_history.py
import uuid
from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime
from sqlalchemy.orm import Session
from sqlalchemy.sql import func
from pydantic import BaseModel

from app.core.database import Base, SessionLocal, engine
from app.ai.llm_models.llm_model import LLMManager


# ==============================
# 🔹 MODELO ORM
# ==============================
class ChatHistory(Base):
    __tablename__ = "chat_history"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    tab = Column(String, nullable=False)
    session_id = Column(String, nullable=False, index=True)
    sender = Column(String, nullable=False)
    message = Column(Text, nullable=False)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())


# ==============================
# 🔹 ESQUEMAS Pydantic
# ==============================
class ChatMessageBase(BaseModel):
    project_id: int
    tab: str
    session_id: str
    sender: str
    message: str


class ChatMessageCreate(ChatMessageBase):
    pass


class ChatMessageResponse(ChatMessageBase):
    id: int
    timestamp: datetime

    class Config:
        from_attributes = True


# ==============================
# 🔹 DEPENDENCIA DB
# ==============================
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ==============================
# 🔹 FUNCIONES AUXILIARES
# ==============================
def save_chat_message(db: Session, project_id: int, tab: str, session_id: str, sender: str, message: str):
    new_msg = ChatHistory(
        project_id=project_id,
        tab=tab,
        session_id=session_id,
        sender=sender,
        message=message,
    )
    db.add(new_msg)
    db.commit()
    db.refresh(new_msg)
    return new_msg


def get_existing_session_id(db: Session, project_id: int, tab: str) -> Optional[str]:
    """Busca si existe una sesión activa para un proyecto y tab."""
    existing = (
        db.query(ChatHistory.session_id)
        .filter(ChatHistory.project_id == project_id, ChatHistory.tab == tab)
        .order_by(ChatHistory.timestamp.desc())
        .first()
    )
    return existing[0] if existing else None


# ==============================
# 🔹 ROUTER FastAPI
# ==============================
router = APIRouter()
llm_manager = LLMManager()


@router.post("/chat/{project_id}/{tab}", response_model=ChatMessageResponse)
def chat_with_ai(
    project_id: int,
    tab: str,
    question: str = Body(..., embed=True),
    db: Session = Depends(get_db),
):
    """Envía un mensaje al chatbot y guarda tanto la pregunta como la respuesta."""
    try:
        session_id = get_existing_session_id(db, project_id, tab) or str(uuid.uuid4())

        # Guardar pregunta del usuario
        save_chat_message(db, project_id, tab, session_id, "user", question)

        # Llamar modelo LLM
        answer = llm_manager.ask(question, session_id)

        # Guardar respuesta del bot
        bot_message = save_chat_message(db, project_id, tab, session_id, "bot", answer)

        return bot_message
        
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Error en el chat: {str(e)}"
        )


@router.get("/{project_id}/{tab}", response_model=List[ChatMessageResponse])
def get_chat_history(project_id: int, tab: str, db: Session = Depends(get_db)):
    """Devuelve el historial de chat de un proyecto, tab y/o sesión específica"""
    messages = (
        db.query(ChatHistory)
        .filter(
            ChatHistory.project_id == project_id,
            ChatHistory.tab == tab
        )
        .order_by(ChatHistory.timestamp.asc())
        .all()
    )
    return messages


@router.delete("/{project_id}/{tab}")
def clear_chat_history(project_id: int, tab: str, db: Session = Depends(get_db)):
    """Elimina todos los mensajes del historial de chat"""
    deleted = (
        db.query(ChatHistory)
        .filter(
            ChatHistory.project_id == project_id,
            ChatHistory.tab == tab
        )
        .delete()
    )
    db.commit()
    if deleted == 0:
        raise HTTPException(status_code=404, detail="No se encontraron mensajes para eliminar")
    return {"message": f"Se eliminaron {deleted} mensajes del chat"}