from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import relationship, Session
from sqlalchemy import Column, Integer, Text, ForeignKey, JSON
from pydantic import BaseModel
from typing import List, Optional

from app.core.database import Base, SessionLocal
from app.models.requirements import (
    Requirement,
    RequirementCreate,
    RequirementResponse
)

# DB Connection
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# SQLAlchemy Model
class RequirementsGeneral(Base):
    __tablename__ = "requirements_general"

    id = Column(Integer, primary_key=True, index=True)

    requirements_analysis = Column(Text)

    project_id = Column(
        Integer,
        ForeignKey("projects.id"),
        nullable=False,
        unique=True
    )

    project = relationship(
        "Project",
        back_populates="requirements_general",
        foreign_keys=[project_id]
    )

    requirements = relationship(
        "Requirement",
        back_populates="requirements_general"
    )



# Pydantic Schemas

class RequirementsGeneralBase(BaseModel):

    requirements_analysis: str
    requirements_analysis: Optional[str] = None


class RequirementsGeneralCreate(RequirementsGeneralBase):

    project_id: int

    requirements: List[RequirementCreate] = []


class RequirementsGeneralResponse(RequirementsGeneralBase):

    id: int

    requirements: List[RequirementResponse] = []

    class Config:
        from_attributes = True


# FastAPI Router

router = APIRouter()


@router.post("/", response_model=RequirementsGeneralResponse)
def create_requirements_general(
    requirement_general: RequirementsGeneralCreate,
    db: Session = Depends(get_db)
):

    db_requirements_general = RequirementsGeneral(
        requirements_analysis=requirement_general.requirements_analysis,
        project_id=requirement_general.project_id
    )

    db.add(db_requirements_general)

    db.flush()


    # Create children requirements

    for r in requirement_general.requirements:

        db_requirement = Requirement(

            good_service_name=r.good_service_name,

            good_service_description=r.good_service_description,

            supply_description=r.supply_description,

            demand_description=r.demand_description,

            unit_of_measure=r.unit_of_measure,

            start_year=r.start_year,

            end_year=r.end_year,

            last_projected_year=r.last_projected_year,

            requirements_general_id=db_requirements_general.id

        )

        db.add(db_requirement)


    db.commit()

    db.refresh(db_requirements_general)

    return db_requirements_general



@router.get("/", response_model=List[RequirementsGeneralResponse])
def get_requirements_general(
    db: Session = Depends(get_db)
):

    return db.query(RequirementsGeneral).all()



@router.get("/{project_id}", response_model=List[RequirementsGeneralResponse])
def get_project_requirements_general(
    project_id: int,
    db: Session = Depends(get_db)
):

    return db.query(RequirementsGeneral).filter(
        RequirementsGeneral.project_id == project_id
    ).all()



@router.delete("/{requirement_general_id}", response_model=dict)
def delete_requirements_general(
    requirement_general_id: int,
    db: Session = Depends(get_db)
):

    requirement_general = db.query(RequirementsGeneral).filter(
        RequirementsGeneral.id == requirement_general_id
    ).first()

    if not requirement_general:

        raise HTTPException(
            status_code=404,
            detail="RequirementsGeneral not found"
        )


    db.delete(requirement_general)

    db.commit()

    return {"message": "RequirementsGeneral deleted"}



@router.put("/{requirement_general_id}", response_model=RequirementsGeneralResponse)
def update_requirements_general(

    requirement_general_id: int,

    updated_data: RequirementsGeneralCreate,

    db: Session = Depends(get_db)

):

    requirement_general = db.query(RequirementsGeneral).filter(
        RequirementsGeneral.id == requirement_general_id
    ).first()


    if not requirement_general:

        raise HTTPException(
            status_code=404,
            detail="RequirementsGeneral not found"
        )


    for key, value in updated_data.dict(
        exclude={"requirements"},
        exclude_unset=True
    ).items():

        setattr(requirement_general, key, value)


    db.commit()

    db.refresh(requirement_general)

    return requirement_general