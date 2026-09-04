"""Persistence and export endpoints for thesis evaluation telemetry."""

from __future__ import annotations

import csv
import io
import os
import subprocess
from datetime import datetime
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, JSON, String
from sqlalchemy.orm import Session
from sqlalchemy.sql import func

from app.ai.rag.config import RAGConfig
from app.core.database import Base, SessionLocal


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def experimental_configuration() -> Dict[str, Any]:
    """Return reproducible runtime settings while deliberately excluding secrets."""
    rag = RAGConfig.from_env()
    commit = os.getenv("MGA_AI_COMMIT", "")
    if not commit:
        try:
            commit = subprocess.check_output(
                ["git", "rev-parse", "HEAD"], cwd=os.path.dirname(__file__), text=True, timeout=1
            ).strip()
        except (OSError, subprocess.SubprocessError):
            commit = None
    provider = os.getenv("LLM_PROVIDER", "groq").lower()
    model_by_provider = {
        "groq": os.getenv("GROQ_MODEL", "llama-3.1-8b-instant"),
        "openai": os.getenv("OPENAI_MODEL", ""),
        "gemini": "gemini-2.5-flash",
        "ollama": os.getenv("OLLAMA_MODEL", ""),
    }
    return {
        "software_version": os.getenv("MGA_AI_VERSION", "1.0.0"),
        "commit": commit,
        "llm_provider": provider,
        "llm_model": model_by_provider.get(provider, ""),
        "rag_enabled": rag.enabled,
        "rag_document": rag.source_document_path.name,
        "rag_chunk_size": rag.chunk_size,
        "rag_overlap": rag.chunk_overlap,
        "rag_top_k": rag.top_k,
        "rag_min_similarity": rag.min_similarity,
    }


class EvaluationSession(Base):
    __tablename__ = "evaluation_sessions"

    id = Column(Integer, primary_key=True)
    participant_id = Column(String(128), nullable=False, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False, index=True)
    started_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    ended_at = Column(DateTime(timezone=True), nullable=True)
    task = Column(String(160), nullable=True)
    completed = Column(Boolean, nullable=True)
    configuration = Column(JSON, nullable=False, default=dict)


class EvaluationEvent(Base):
    __tablename__ = "evaluation_events"

    id = Column(Integer, primary_key=True)
    evaluation_session_id = Column(Integer, ForeignKey("evaluation_sessions.id", ondelete="CASCADE"), nullable=False, index=True)
    occurred_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    section = Column(String(80), nullable=True)
    event_type = Column(String(80), nullable=False)
    task = Column(String(160), nullable=True)
    llm_duration_ms = Column(Integer, nullable=True)
    rag_enabled = Column(Boolean, nullable=True)
    payload = Column(JSON, nullable=False, default=dict)


class EvaluationSessionCreate(BaseModel):
    participant_id: str = Field(min_length=1, max_length=128)
    project_id: int
    task: Optional[str] = Field(default=None, max_length=160)


class EvaluationSessionFinish(BaseModel):
    completed: bool


class EvaluationEventCreate(BaseModel):
    section: Optional[str] = Field(default=None, max_length=80)
    event_type: str = Field(min_length=1, max_length=80)
    task: Optional[str] = Field(default=None, max_length=160)
    llm_duration_ms: Optional[int] = Field(default=None, ge=0)
    rag_enabled: Optional[bool] = None
    payload: Dict[str, Any] = Field(default_factory=dict)


class EvaluationSessionResponse(BaseModel):
    id: int
    participant_id: str
    project_id: int
    started_at: datetime
    ended_at: Optional[datetime]
    task: Optional[str]
    completed: Optional[bool]
    configuration: Dict[str, Any]

    model_config = {"from_attributes": True}


router = APIRouter(prefix="/evaluation", tags=["Evaluation"])


def _session_or_404(db: Session, evaluation_session_id: int) -> EvaluationSession:
    session = db.query(EvaluationSession).filter_by(id=evaluation_session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Sesión de evaluación no encontrada")
    return session


@router.get("/configuration")
def get_experimental_configuration():
    return experimental_configuration()


@router.post("/sessions", response_model=EvaluationSessionResponse, status_code=201)
def start_evaluation_session(data: EvaluationSessionCreate, db: Session = Depends(get_db)):
    record = EvaluationSession(
        participant_id=data.participant_id,
        project_id=data.project_id,
        task=data.task,
        configuration=experimental_configuration(),
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


@router.post("/sessions/{evaluation_session_id}/events", status_code=201)
def record_evaluation_event(evaluation_session_id: int, data: EvaluationEventCreate, db: Session = Depends(get_db)):
    _session_or_404(db, evaluation_session_id)
    event = EvaluationEvent(evaluation_session_id=evaluation_session_id, **data.model_dump())
    db.add(event)
    db.commit()
    return {"id": event.id}


@router.get("/sessions/{evaluation_session_id}", response_model=EvaluationSessionResponse)
def get_evaluation_session(evaluation_session_id: int, db: Session = Depends(get_db)):
    return _session_or_404(db, evaluation_session_id)


@router.post("/sessions/{evaluation_session_id}/finish", response_model=EvaluationSessionResponse)
def finish_evaluation_session(evaluation_session_id: int, data: EvaluationSessionFinish, db: Session = Depends(get_db)):
    record = _session_or_404(db, evaluation_session_id)
    record.ended_at = datetime.utcnow()
    record.completed = data.completed
    db.commit()
    db.refresh(record)
    return record


@router.get("/sessions")
def list_evaluation_sessions(db: Session = Depends(get_db)):
    sessions = db.query(EvaluationSession).order_by(EvaluationSession.started_at.desc()).all()
    result: List[Dict[str, Any]] = []
    for record in sessions:
        events = db.query(EvaluationEvent).filter_by(evaluation_session_id=record.id).all()
        validation_events = [event for event in events if event.event_type == "validation_run"]
        latest_validation = {}
        for event in validation_events:
            latest_validation[event.section] = event
        result.append({
            "id": record.id,
            "participant_id": record.participant_id,
            "project_id": record.project_id,
            "started_at": record.started_at,
            "ended_at": record.ended_at,
            "task": record.task,
            "completed": record.completed,
            "configuration": record.configuration,
            "llm_queries": sum(event.event_type == "llm_query" for event in events),
            "corrections": sum(event.event_type == "suggestion_accepted" for event in events),
            "field_saves": sum(event.event_type == "field_saved" for event in events),
            "validation_errors_found": sum(int((event.payload or {}).get("errors_count", 0)) for event in validation_events),
            "validation_errors_remaining": sum(int((event.payload or {}).get("errors_count", 0)) for event in latest_validation.values()),
            "sections_completed": sum(bool((event.payload or {}).get("completed")) for event in latest_validation.values()),
            "tasks_completed": sum(event.event_type == "task_completed" for event in events),
            "events": [{"section": event.section, "event_type": event.event_type, "task": event.task, "llm_duration_ms": event.llm_duration_ms, "rag_enabled": event.rag_enabled, "payload": event.payload, "occurred_at": event.occurred_at} for event in events],
        })
    return result


@router.get("/export")
def export_evaluation_sessions(format: str = "csv", db: Session = Depends(get_db)):
    records = list_evaluation_sessions(db)
    if format.lower() == "json":
        return records
    if format.lower() != "csv":
        raise HTTPException(status_code=422, detail="format debe ser csv o json")
    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=["session_id", "participant_id", "project_id", "started_at", "ended_at", "task", "completed", "llm_queries", "corrections", "field_saves", "validation_errors_found", "validation_errors_remaining", "sections_completed", "tasks_completed", "software_version", "llm_provider", "llm_model", "rag_enabled", "event_time", "section", "event_type", "event_task", "llm_duration_ms", "event_payload"])
    writer.writeheader()
    for record in records:
        base = {"session_id": record["id"], "participant_id": record["participant_id"], "project_id": record["project_id"], "started_at": record["started_at"], "ended_at": record["ended_at"], "task": record["task"], "completed": record["completed"], "llm_queries": record["llm_queries"], "corrections": record["corrections"], "field_saves": record["field_saves"], "validation_errors_found": record["validation_errors_found"], "validation_errors_remaining": record["validation_errors_remaining"], "sections_completed": record["sections_completed"], "tasks_completed": record["tasks_completed"], "software_version": record["configuration"].get("software_version"), "llm_provider": record["configuration"].get("llm_provider"), "llm_model": record["configuration"].get("llm_model"), "rag_enabled": record["configuration"].get("rag_enabled")}
        for event in record["events"] or [{}]:
            writer.writerow({**base, "event_time": event.get("occurred_at"), "section": event.get("section"), "event_type": event.get("event_type"), "event_task": event.get("task"), "llm_duration_ms": event.get("llm_duration_ms"), "event_payload": event.get("payload")})
    return StreamingResponse(iter([output.getvalue()]), media_type="text/csv", headers={"Content-Disposition": "attachment; filename=evaluation_telemetry.csv"})