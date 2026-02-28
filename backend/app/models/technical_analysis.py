from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import relationship, Session
from sqlalchemy import Column, Integer, Text, ForeignKey
from pydantic import BaseModel
from typing import List, Optional

from app.core.database import Base, SessionLocal


# ==========================
# DATABASE CONNECTION
# ==========================

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ==========================
# SQLALCHEMY MODEL
# ==========================

class TechnicalAnalysis(Base):
    __tablename__ = "technical_analysis"

    id = Column(Integer, primary_key=True, index=True)

    analysis = Column(Text, nullable=True)

    project_id = Column(
        Integer,
        ForeignKey("projects.id"),
        nullable=False,
        unique=True
    )

    project = relationship(
        "Project",
        back_populates="technical_analysis"
    )


# ==========================
# PYDANTIC SCHEMAS
# ==========================

class TechnicalAnalysisBase(BaseModel):
    analysis: Optional[str] = None


class TechnicalAnalysisCreate(TechnicalAnalysisBase):
    project_id: int


class TechnicalAnalysisResponse(TechnicalAnalysisBase):
    id: int
    project_id: int

    class Config:
        from_attributes = True


# ==========================
# ROUTER
# ==========================

router = APIRouter()


# ==========================
# CREATE
# ==========================

@router.post("/", response_model=TechnicalAnalysisResponse)
def create_technical_analysis(
    technical_analysis: TechnicalAnalysisCreate,
    db: Session = Depends(get_db)
):
    existing = db.query(TechnicalAnalysis).filter(
        TechnicalAnalysis.project_id == technical_analysis.project_id
    ).first()

    if existing:
        raise HTTPException(
            status_code=400,
            detail="TechnicalAnalysis already exists for this project"
        )

    db_technical_analysis = TechnicalAnalysis(
        analysis=technical_analysis.analysis,
        project_id=technical_analysis.project_id
    )

    db.add(db_technical_analysis)
    db.commit()
    db.refresh(db_technical_analysis)

    return db_technical_analysis


# ==========================
# GET ALL
# ==========================

@router.get("/", response_model=List[TechnicalAnalysisResponse])
def get_technical_analysis(db: Session = Depends(get_db)):
    return db.query(TechnicalAnalysis).all()


# ==========================
# GET BY PROJECT
# ==========================

@router.get("/project/{project_id}", response_model=TechnicalAnalysisResponse)
def get_project_technical_analysis(
    project_id: int,
    db: Session = Depends(get_db)
):
    technical_analysis = db.query(TechnicalAnalysis).filter(
        TechnicalAnalysis.project_id == project_id
    ).first()

    if not technical_analysis:
        raise HTTPException(
            status_code=404,
            detail="TechnicalAnalysis not found"
        )

    return technical_analysis


# ==========================
# UPDATE
# ==========================

@router.put("/{technical_analysis_id}", response_model=TechnicalAnalysisResponse)
def update_technical_analysis(
    technical_analysis_id: int,
    updated_data: TechnicalAnalysisBase,
    db: Session = Depends(get_db)
):
    technical_analysis = db.query(TechnicalAnalysis).filter(
        TechnicalAnalysis.id == technical_analysis_id
    ).first()

    if not technical_analysis:
        raise HTTPException(
            status_code=404,
            detail="TechnicalAnalysis not found"
        )

    technical_analysis.analysis = updated_data.analysis

    db.commit()
    db.refresh(technical_analysis)

    return technical_analysis


# ==========================
# DELETE
# ==========================

@router.delete("/{technical_analysis_id}")
def delete_technical_analysis(
    technical_analysis_id: int,
    db: Session = Depends(get_db)
):
    technical_analysis = db.query(TechnicalAnalysis).filter(
        TechnicalAnalysis.id == technical_analysis_id
    ).first()

    if not technical_analysis:
        raise HTTPException(
            status_code=404,
            detail="TechnicalAnalysis not found"
        )

    db.delete(technical_analysis)
    db.commit()

    return {"message": "TechnicalAnalysis deleted"}