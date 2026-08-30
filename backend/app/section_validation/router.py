from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.ai.context.module_dependencies import UnknownSectionError
from app.core.database import SessionLocal
from app.models.project import Project

from .schemas import SectionValidationResult
from .service import SectionValidationService


router = APIRouter()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def _ensure_project(db: Session, project_id: int) -> None:
    if not db.query(Project.id).filter(Project.id == project_id).first():
        raise HTTPException(status_code=404, detail="Proyecto no encontrado")


@router.get("/{project_id}/sections/validation", response_model=List[SectionValidationResult])
def validate_all_sections(project_id: int, db: Session = Depends(get_db)):
    _ensure_project(db, project_id)
    return SectionValidationService(db).validate_all(project_id)


@router.get("/{project_id}/sections/{section}/validation", response_model=SectionValidationResult)
def validate_section(project_id: int, section: str, db: Session = Depends(get_db)):
    _ensure_project(db, project_id)
    try:
        return SectionValidationService(db).validate_section(project_id, section)
    except UnknownSectionError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc