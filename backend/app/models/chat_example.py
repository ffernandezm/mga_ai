"""
Ejemplo de integración del LLM Manager en un endpoint FastAPI

Este archivo muestra cómo usar el LLM Manager en tus rutas.
Puedes copiarlo como referencia para tus endpoints.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
import uuid

from app.core.database import SessionLocal
from app.ai.llm_models.llm_manager import LLMManager
from app.models.chat_history import save_chat_message

# ==============================
# 🔹 ESQUEMAS PYDANTIC
# ==============================

class ChatRequest(BaseModel):
    """Solicitud de chat"""
    message: str
    tab: str  # ej: "problems", "objectives", "alternatives"
    session_id: Optional[str] = None  # Si no se proporciona, se genera uno


class ChatResponse(BaseModel):
    """Respuesta de chat"""
    response: str
    session_id: str
    timestamp: str


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
# 🔹 INICIALIZAR LLM MANAGER (una sola vez)
# ==============================

# ⚠️ IMPORTANTE: Esto se ejecuta UNA sola vez al iniciar la app
# Ver al final para integración con FastAPI lifespan
llm_manager = LLMManager()  # Usa el proveedor de .env


# ==============================
# 🔹 RUTAS DE CHAT
# ==============================

router = APIRouter()


@router.post("/chat/{project_id}", response_model=ChatResponse)
def chat(
    project_id: int,
    request: ChatRequest,
    db: Session = Depends(get_db)
):
    """
    Endpoint de chat con IA para asistencia en formularios MGA
    
    Args:
        project_id: ID del proyecto
        request: ChatRequest con mensaje, tab, y session_id (opcional)
        db: Sesión de base de datos
    
    Returns:
        ChatResponse con la respuesta del LLM
    
    Ejemplo de uso:
    ```
    POST /chat/1
    {
        "message": "¿Cómo defino un problema central?",
        "tab": "problems",
        "session_id": "session_abc123"
    }
    ```
    """
    try:
        # Generar session_id si no se proporciona
        session_id = request.session_id or str(uuid.uuid4())
        
        # Guardar mensaje del usuario en BD
        save_chat_message(
            db=db,
            project_id=project_id,
            tab=request.tab,
            session_id=session_id,
            sender="user",
            message=request.message
        )
        
        # Obtener respuesta del LLM
        response_text = llm_manager.ask(
            question=request.message,
            session_id=session_id,
            tab=request.tab,
            project_id=project_id,
            db=db
        )
        
        # Guardar respuesta del bot en BD
        save_chat_message(
            db=db,
            project_id=project_id,
            tab=request.tab,
            session_id=session_id,
            sender="bot",
            message=response_text
        )
        
        return ChatResponse(
            response=response_text,
            session_id=session_id,
            timestamp=str(__import__("datetime").datetime.now().__import__("datetime").timezone.utc)
        )
    
    except Exception as e:
        print(f"❌ Error en chat: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/chat/{project_id}/{tab}/history")
def get_chat_history(
    project_id: int,
    tab: str,
    session_id: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    Obtener historial de chat de un proyecto/tab
    
    Args:
        project_id: ID del proyecto
        tab: Pestaña (ej: "problems")
        session_id: (Opcional) ID de sesión específica
        db: Sesión de base de datos
    
    Returns:
        Lista de mensajes del chat
    """
    try:
        from app.models.chat_history import ChatHistory
        
        query = db.query(ChatHistory).filter(
            ChatHistory.project_id == project_id,
            ChatHistory.tab == tab
        )
        
        if session_id:
            query = query.filter(ChatHistory.session_id == session_id)
        
        messages = query.order_by(ChatHistory.timestamp.asc()).all()
        
        return {
            "project_id": project_id,
            "tab": tab,
            "session_id": session_id,
            "messages": [
                {
                    "id": msg.id,
                    "sender": msg.sender,
                    "message": msg.message,
                    "timestamp": msg.timestamp.isoformat() if msg.timestamp else None
                }
                for msg in messages
            ]
        }
    
    except Exception as e:
        print(f"❌ Error obteniendo historial: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ==============================
# 🔹 INTEGRACIÓN CON STARTUP (Opcional)
# ==============================

# Si quieres inicializar el LLM Manager en el startup de FastAPI:
# 
# from contextlib import asynccontextmanager
# 
# @asynccontextmanager
# async def lifespan(app: FastAPI):
#     # Startup
#     global llm_manager
#     llm_manager = LLMManager()
#     print(f"✅ LLM Manager inicializado ({llm_manager.llm_provider})")
#     yield
#     # Shutdown
#     print("🛑 Cerrando LLM Manager")
# 
# app = FastAPI(lifespan=lifespan)
