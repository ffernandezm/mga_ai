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

    project = relationship("Project", back_populates="chat_history")


# Relación inversa en Project
from .project import Project
Project.chat_history = relationship("ChatHistory", back_populates="project", cascade="all, delete-orphan")


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

@router.get("/{project_id}/{model_name}")
def get_chat_history(project_id: int, model_name: str, db: Session = Depends(get_db)):
    # Verificar si la tabla existe
    if model_name not in Base.metadata.tables:
        raise HTTPException(status_code=404, detail=f"Modelo {model_name} no encontrado")

    table = Base.metadata.tables[model_name]

    # Buscar registro asociado al proyecto
    stmt = select(table).where(table.c.project_id == project_id)
    result = db.execute(stmt).first()

    if not result:
        raise HTTPException(status_code=404, detail=f"No hay registros en {model_name} para el proyecto {project_id}")

    row = result._mapping  # acceder como dict-like

    # Verificar si existe el campo chat_history
    if "chat_history" not in row:
        raise HTTPException(status_code=400, detail=f"El modelo {model_name} no tiene campo chat_history")

    return row["chat_history"]