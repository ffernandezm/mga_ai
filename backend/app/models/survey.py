from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, relationship
from app.core.database import Base, SessionLocal
from sqlalchemy import Column, Integer, Text, ForeignKey, JSON
from pydantic import BaseModel
from typing import List, Dict, Any, Optional

# 🔹 Conexión DB
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# 🔹 Modelo SQLAlchemy
class Survey(Base):
    __tablename__ = "survey"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    project = relationship("Project", back_populates="survey")
    survey_json = Column(JSON, nullable=False)


# 🔹 Esquemas Pydantic
class SurveyBase(BaseModel):
    survey_json: Dict[str, Any]


class SurveyCreate(SurveyBase):
    pass


class SurveyUpdate(SurveyBase):
    pass


class SurveyResponse(SurveyBase):
    id: int
    project_id: int

    class Config:
        from_attributes = True


router = APIRouter()


@router.post("/{project_id}", response_model=SurveyResponse)
def create_survey(project_id: int, survey: SurveyCreate, db: Session = Depends(get_db)):
    db_survey = Survey(project_id=project_id, survey_json=survey.survey_json)
    db.add(db_survey)
    db.commit()
    db.refresh(db_survey)
    return db_survey



@router.get("/{project_id}", response_model=List[SurveyResponse])
def get_survey_by_project(project_id: int, db: Session = Depends(get_db)):
    return db.query(Survey).filter(Survey.project_id == project_id).all()



@router.get("/survey", response_model=List[SurveyResponse])
def get_all_survey(db: Session = Depends(get_db)):
    return db.query(Survey).all()



@router.put("/{project_id}/{survey_id}", response_model=SurveyResponse)
def update_survey(project_id: int, survey_id: int, survey: SurveyUpdate, db: Session = Depends(get_db)):
    db_survey = (
        db.query(Survey)
        .filter(Survey.project_id == project_id, Survey.id == survey_id)
        .first()
    )
    if not db_survey:
        raise HTTPException(status_code=404, detail="Survey not found for this project")

    db_survey.survey_json = survey.survey_json
    db.commit()
    db.refresh(db_survey)
    return db_survey


@router.delete("/{project_id}/{survey_id}", response_model=dict)
def delete_survey(project_id: int, survey_id: int, db: Session = Depends(get_db)):
    db_survey = (
        db.query(Survey)
        .filter(Survey.project_id == project_id, Survey.id == survey_id)
        .first()
    )
    if not db_survey:
        raise HTTPException(status_code=404, detail="Survey not found for this project")

    db.delete(db_survey)
    db.commit()
    return {"message": "Survey deleted successfully"}
