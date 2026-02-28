from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import relationship, Session
from sqlalchemy import Column, Integer, Text, ForeignKey
from pydantic import BaseModel
from typing import List

from app.core.database import Base, SessionLocal


# DB Connection

def get_db():

    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()



# SQLAlchemy Model

class Requirement(Base):

    __tablename__ = "requirements"


    id = Column(Integer, primary_key=True)


    good_service_name = Column(Text)

    good_service_description = Column(Text)

    supply_description = Column(Text)

    demand_description = Column(Text)

    unit_of_measure = Column(Text)


    start_year = Column(Integer)

    end_year = Column(Integer)

    last_projected_year = Column(Integer)


    requirements_general_id = Column(

        Integer,

        ForeignKey("requirements_general.id"),

        nullable=False

    )


    requirements_general = relationship(

        "RequirementsGeneral",

        back_populates="requirements"

    )



# Pydantic Schemas


class RequirementBase(BaseModel):

    good_service_name: str

    good_service_description: str

    supply_description: str

    demand_description: str

    unit_of_measure: str

    start_year: int

    end_year: int

    last_projected_year: int



class RequirementCreate(RequirementBase):

    requirements_general_id: int



class RequirementResponse(RequirementBase):

    id: int

    requirements_general_id: int


    model_config = {

        "from_attributes": True

    }



# FastAPI Router

router = APIRouter()



@router.post("/", response_model=RequirementResponse)
def create_requirement(

    requirement: RequirementCreate,

    db: Session = Depends(get_db)

):

    from app.models.requirements_general import RequirementsGeneral


    parent = db.query(RequirementsGeneral).filter(

        RequirementsGeneral.id == requirement.requirements_general_id

    ).first()


    if not parent:

        raise HTTPException(

            status_code=400,

            detail="RequirementsGeneral with given ID does not exist"

        )


    db_requirement = Requirement(**requirement.dict())


    db.add(db_requirement)

    db.commit()

    db.refresh(db_requirement)

    return db_requirement



@router.get("/", response_model=List[RequirementResponse])
def get_requirements(

    db: Session = Depends(get_db)

):

    return db.query(Requirement).all()



@router.get("/{project_id}", response_model=List[RequirementResponse])
def get_project_requirements(

    project_id: int,

    db: Session = Depends(get_db)

):

    requirements = db.query(Requirement).join(

        Requirement.requirements_general

    ).filter(

        Requirement.requirements_general.has(

            project_id=project_id

        )

    ).all()


    if not requirements:

        raise HTTPException(

            status_code=404,

            detail="No requirements found for this project"

        )


    return requirements



@router.delete("/{requirement_id}", response_model=dict)
def delete_requirement(

    requirement_id: int,

    db: Session = Depends(get_db)

):

    requirement = db.query(Requirement).filter(

        Requirement.id == requirement_id

    ).first()


    if not requirement:

        raise HTTPException(

            status_code=404,

            detail="Requirement not found"

        )


    db.delete(requirement)

    db.commit()


    return {"message": "Requirement deleted"}



@router.put("/{requirement_id}", response_model=RequirementResponse)
def update_requirement(

    requirement_id: int,

    updated_data: RequirementCreate,

    db: Session = Depends(get_db)

):

    requirement = db.query(Requirement).filter(

        Requirement.id == requirement_id

    ).first()


    if not requirement:

        raise HTTPException(

            status_code=404,

            detail="Requirement not found"

        )


    for key, value in updated_data.dict().items():

        setattr(requirement, key, value)


    db.commit()

    db.refresh(requirement)

    return requirement