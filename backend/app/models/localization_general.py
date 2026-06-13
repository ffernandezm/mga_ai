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

FIELD_LABELS = {"administrative_political_factors": "Factores Político-Administrativos",
                "proximity_to_target_population": "Proximidad a la Población Objetivo",
                "proximity_to_supply_sources": "Proximidad a Fuentes de Abastecimiento",
                "communications": "Comunicaciones",
                "land_cost_and_availability": "Costo y Disponibilidad de Terreno",
                "public_services_availability": "Disponibilidad de Servicios Públicos",
                "labor_availability_and_cost": "Disponibilidad y Costo de Mano de Obra",
                "tax_and_legal_structure": "Estructura Fiscal y Legal",
                "environmental_factors": "Factores Ambientales",
                "gender_equity_impact": "Impacto en la Equidad de Género",
                "transport_means_and_costs": "Medios de Transporte y Costos",
                "public_order": "Orden Público",
                "other_factors": "Otros Factores",
                "topography": "Topografía"}


# ==========================
# SQLAlchemy Model
# ==========================

class LocalizationGeneral(Base):
    __tablename__ = "localization_general"
    __table_args__ = {
        "info": {
            "label_plural": "Localización General",
            "label_singular": "Localización General",
        }
    }

    id = Column(Integer, primary_key=True, index=True)

    # 14 Boolean Fields
    administrative_political_factors = Column(Boolean, default=False, info={"label": FIELD_LABELS["administrative_political_factors"]})
    proximity_to_target_population = Column(Boolean, default=False, info={"label": FIELD_LABELS["proximity_to_target_population"]})
    proximity_to_supply_sources = Column(Boolean, default=False, info={"label": FIELD_LABELS["proximity_to_supply_sources"]})
    communications = Column(Boolean, default=False, info={"label": FIELD_LABELS["communications"]})
    land_cost_and_availability = Column(Boolean, default=False, info={"label": FIELD_LABELS["land_cost_and_availability"]})
    public_services_availability = Column(Boolean, default=False, info={"label": FIELD_LABELS["public_services_availability"]})
    labor_availability_and_cost = Column(Boolean, default=False, info={"label": FIELD_LABELS["labor_availability_and_cost"]})
    tax_and_legal_structure = Column(Boolean, default=False, info={"label": FIELD_LABELS["tax_and_legal_structure"]})
    environmental_factors = Column(Boolean, default=False, info={"label": FIELD_LABELS["environmental_factors"]})
    gender_equity_impact = Column(Boolean, default=False, info={"label": FIELD_LABELS["gender_equity_impact"]})
    transport_means_and_costs = Column(Boolean, default=False, info={"label": FIELD_LABELS["transport_means_and_costs"]})
    public_order = Column(Boolean, default=False, info={"label": FIELD_LABELS["public_order"]})
    other_factors = Column(Boolean, default=False, info={"label": FIELD_LABELS["other_factors"]})
    topography = Column(Boolean, default=False, info={"label": FIELD_LABELS["topography"]})

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