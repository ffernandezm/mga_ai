from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import relationship, Session
from sqlalchemy import Column, Integer, Boolean, ForeignKey
from pydantic import BaseModel
from typing import List, Optional

from app.core.database import Base, SessionLocal
from app.models.localization import LocalizationResponse


# ==========================
# DB Connection
# ==========================

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ==========================
# SQLAlchemy Model
# ==========================

class LocalizationGeneral(Base):
    __tablename__ = "localization_general"

    id = Column(Integer, primary_key=True, index=True)

    # 14 Boolean Fields
    administrative_political_factors = Column(Boolean, default=False)
    proximity_to_target_population = Column(Boolean, default=False)
    proximity_to_supply_sources = Column(Boolean, default=False)
    communications = Column(Boolean, default=False)
    land_cost_and_availability = Column(Boolean, default=False)
    public_services_availability = Column(Boolean, default=False)
    labor_availability_and_cost = Column(Boolean, default=False)
    tax_and_legal_structure = Column(Boolean, default=False)
    environmental_factors = Column(Boolean, default=False)
    gender_equity_impact = Column(Boolean, default=False)
    transport_means_and_costs = Column(Boolean, default=False)
    public_order = Column(Boolean, default=False)
    other_factors = Column(Boolean, default=False)
    topography = Column(Boolean, default=False)

    project_id = Column(
        Integer,
        ForeignKey("projects.id"),
        nullable=False,
        unique=True
    )

    project = relationship(
        "Project",
        back_populates="localization_general"
    )

    localizations = relationship(
        "Localization",
        back_populates="localization_general",
        cascade="all, delete-orphan"
    )


# ==========================
# Schemas
# ==========================

class LocalizationGeneralBase(BaseModel):
    administrative_political_factors: Optional[bool] = False
    proximity_to_target_population: Optional[bool] = False
    proximity_to_supply_sources: Optional[bool] = False
    communications: Optional[bool] = False
    land_cost_and_availability: Optional[bool] = False
    public_services_availability: Optional[bool] = False
    labor_availability_and_cost: Optional[bool] = False
    tax_and_legal_structure: Optional[bool] = False
    environmental_factors: Optional[bool] = False
    gender_equity_impact: Optional[bool] = False
    transport_means_and_costs: Optional[bool] = False
    public_order: Optional[bool] = False
    other_factors: Optional[bool] = False
    topography: Optional[bool] = False


class LocalizationGeneralUpdate(LocalizationGeneralBase):
    pass


class LocalizationGeneralResponse(LocalizationGeneralBase):
    id: int
    localizations: List[LocalizationResponse] = []

    model_config = {
        "from_attributes": True
    }


# ==========================
# Router
# ==========================

router = APIRouter()


@router.get("/project/{project_id}", response_model=LocalizationGeneralResponse)
def get_project_localization_general(
    project_id: int,
    db: Session = Depends(get_db)
):
    localization_general = db.query(LocalizationGeneral).filter(
        LocalizationGeneral.project_id == project_id
    ).first()

    if not localization_general:
        raise HTTPException(
            status_code=404,
            detail="LocalizationGeneral not found"
        )

    return localization_general


@router.put("/project/{project_id}", response_model=LocalizationGeneralResponse)
def update_localization_general(
    project_id: int,
    updated_data: LocalizationGeneralUpdate,
    db: Session = Depends(get_db)
):

    localization_general = db.query(LocalizationGeneral).filter(
        LocalizationGeneral.project_id == project_id
    ).first()

    if not localization_general:
        raise HTTPException(
            status_code=404,
            detail="LocalizationGeneral not found"
        )

    for key, value in updated_data.model_dump(exclude_unset=True).items():
        setattr(localization_general, key, value)

    db.commit()
    db.refresh(localization_general)

    return localization_general