from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import relationship, Session, joinedload
from sqlalchemy import Column, Integer, Text, ForeignKey
from pydantic import BaseModel
from typing import List, Optional

from app.core.database import Base, SessionLocal


# DB Connection

def get_db():

    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()

FIELD_LABELS = {"good_service_name": "Nombre del Bien o Servicio",
                "good_service_description": "Descripción del Bien o Servicio",
                "supply_description": "Descripción de la Oferta",
                "demand_description": "Descripción de la Demanda",
                "unit_of_measure": "Unidad de Medida",
                "start_year": "Año de Inicio",
                "end_year": "Año de Fin",
                "last_projected_year": "Último Año Proyectado"}


# SQLAlchemy Model

class Requirement(Base):

    __tablename__ = "requirements"
    __table_args__ = {
        "info": {
            "label_plural": "Requerimientos",
            "label_singular": "Requerimiento",
        }
    }


    id = Column(Integer, primary_key=True)


    good_service_name = Column(Text, info={"label": FIELD_LABELS["good_service_name"]})

    good_service_description = Column(Text, info={"label": FIELD_LABELS["good_service_description"]})

    supply_description = Column(Text, info={"label": FIELD_LABELS["supply_description"]})

    demand_description = Column(Text, info={"label": FIELD_LABELS["demand_description"]})

    unit_of_measure = Column(Text, info={"label": FIELD_LABELS["unit_of_measure"]})


    start_year = Column(Integer, info={"label": FIELD_LABELS["start_year"]})

    end_year = Column(Integer, info={"label": FIELD_LABELS["end_year"]})

    last_projected_year = Column(Integer, info={"label": FIELD_LABELS["last_projected_year"]})


    requirements_general_id = Column(

        Integer,

        ForeignKey("requirements_general.id"),

        nullable=False

    )


    requirements_general = relationship(

        "RequirementsGeneral",

        back_populates="requirements"

    )

    @property
    def requirements_analysis(self) -> Optional[str]:
        if self.requirements_general is None:
            return None
        return self.requirements_general.requirements_analysis



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

    requirements_analysis: Optional[str] = None


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

    return db.query(Requirement).options(
        joinedload(Requirement.requirements_general)
    ).all()



@router.get("/{project_id}", response_model=List[RequirementResponse])
def get_project_requirements(

    project_id: int,

    db: Session = Depends(get_db)

):

    requirements = db.query(Requirement).join(

        Requirement.requirements_general

    ).options(

        joinedload(Requirement.requirements_general)

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