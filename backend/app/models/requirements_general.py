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
        back_populates="requirements_general",
        cascade="all, delete-orphan"
    )



# Pydantic Schemas

class RequirementsGeneralBase(BaseModel):
    requirements_analysis: Optional[str] = None
    # Campo legacy en frontend: se mantiene por compatibilidad.
    analysis: Optional[str] = None


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
    analysis_value = (
        requirement_general.requirements_analysis
        if requirement_general.requirements_analysis is not None
        else requirement_general.analysis
    )

    # `project_id` es unico: si ya existe, actualizar en vez de intentar insertar.
    db_requirements_general = db.query(RequirementsGeneral).filter(
        RequirementsGeneral.project_id == requirement_general.project_id
    ).first()

    if db_requirements_general is None:
        db_requirements_general = RequirementsGeneral(
            requirements_analysis=analysis_value,
            project_id=requirement_general.project_id,
        )
        db.add(db_requirements_general)
        db.flush()
    else:
        db_requirements_general.requirements_analysis = analysis_value
        # Reemplazar detalle completo para que el POST sea idempotente.
        db.query(Requirement).filter(
            Requirement.requirements_general_id == db_requirements_general.id
        ).delete(synchronize_session=False)
        db.flush()

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
            requirements_general_id=db_requirements_general.id,
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



@router.get("/{project_id}", response_model=RequirementsGeneralResponse)
def get_project_requirements_general(
    project_id: int,
    db: Session = Depends(get_db)
):

    record = db.query(RequirementsGeneral).filter(
        RequirementsGeneral.project_id == project_id
    ).first()

    if not record:
        raise HTTPException(status_code=404, detail="RequirementsGeneral not found")

    return record



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

    # Compatibilidad: permitir actualizar usando project_id en la URL.
    if not requirement_general:
        requirement_general = db.query(RequirementsGeneral).filter(
            RequirementsGeneral.project_id == requirement_general_id
        ).first()


    if not requirement_general:

        raise HTTPException(
            status_code=404,
            detail="RequirementsGeneral not found"
        )


    update_data = updated_data.dict(
        exclude={"requirements"},
        exclude_unset=True
    )

    if "analysis" in update_data and "requirements_analysis" not in update_data:
        update_data["requirements_analysis"] = update_data["analysis"]

    update_data.pop("analysis", None)

    for key, value in update_data.items():

        setattr(requirement_general, key, value)


    db.commit()

    db.refresh(requirement_general)

    return requirement_general