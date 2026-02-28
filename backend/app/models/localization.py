from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import relationship, Session
from sqlalchemy import Column, Integer, Text, ForeignKey, Boolean, Float
from pydantic import BaseModel
from typing import List, Optional

from app.core.database import Base, SessionLocal


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

class Localization(Base):
    __tablename__ = "localization"

    id = Column(Integer, primary_key=True)

    region = Column(Text, nullable=True)
    department = Column(Text, nullable=True)
    city = Column(Text, nullable=True)
    type_group = Column(Text, nullable=True)
    group = Column(Text, nullable=True)
    entity = Column(Text, nullable=True)

    georeferencing = Column(Boolean, default=True)

    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)

    localization_general_id = Column(
        Integer,
        ForeignKey("localization_general.id"),
        nullable=False
    )

    localization_general = relationship(
        "LocalizationGeneral",
        back_populates="localizations"
    )


# ==========================
# Pydantic Schemas
# ==========================

class LocalizationBase(BaseModel):

    region: str
    department: str
    city: str
    type_group: str
    group: str
    entity: str
    georeferencing: bool
    latitude: Optional[float] = None
    longitude: Optional[float] = None


class LocalizationCreate(LocalizationBase):

    localization_general_id: int


class LocalizationResponse(LocalizationBase):

    id: int
    localization_general_id: int

    model_config = {
        "from_attributes": True
    }


# ==========================
# Router
# ==========================

router = APIRouter()


@router.post("/", response_model=LocalizationResponse)
def create_localization(
    localization: LocalizationCreate,
    db: Session = Depends(get_db)
):

    from app.models.localization_general import LocalizationGeneral

    parent = db.query(LocalizationGeneral).filter(
        LocalizationGeneral.id == localization.localization_general_id
    ).first()

    if not parent:
        raise HTTPException(
            status_code=400,
            detail="LocalizationGeneral with given ID does not exist"
        )

    # Validación lógica mínima
    if localization.georeferencing:
        if localization.latitude is None or localization.longitude is None:
            raise HTTPException(
                status_code=400,
                detail="Latitud and Longitud are required when georreferenciacion is True"
            )

    db_localization = Localization(**localization.dict())

    db.add(db_localization)
    db.commit()
    db.refresh(db_localization)

    return db_localization


@router.get("/", response_model=List[LocalizationResponse])
def get_localizations(
    db: Session = Depends(get_db)
):
    return db.query(Localization).all()


@router.get("/{project_id}", response_model=List[LocalizationResponse])
def get_project_localizations(
    project_id: int,
    db: Session = Depends(get_db)
):

    localizations = db.query(Localization).join(
        Localization.localization_general
    ).filter(
        Localization.localization_general.has(
            project_id=project_id
        )
    ).all()

    if not localizations:
        raise HTTPException(
            status_code=404,
            detail="No localizations found for this project"
        )

    return localizations


@router.delete("/{localization_id}", response_model=dict)
def delete_localization(
    localization_id: int,
    db: Session = Depends(get_db)
):

    localization = db.query(Localization).filter(
        Localization.id == localization_id
    ).first()

    if not localization:
        raise HTTPException(
            status_code=404,
            detail="Localization not found"
        )

    db.delete(localization)
    db.commit()

    return {"message": "Localization deleted"}


@router.put("/{localization_id}", response_model=LocalizationResponse)
def update_localization(
    localization_id: int,
    updated_data: LocalizationCreate,
    db: Session = Depends(get_db)
):

    localization = db.query(Localization).filter(
        Localization.id == localization_id
    ).first()

    if not localization:
        raise HTTPException(
            status_code=404,
            detail="Localization not found"
        )

    if updated_data.georeferencing:
        if updated_data.latitude is None or updated_data.longitude is None:
            raise HTTPException(
                status_code=400,
                detail="Latitud and Longitud are required when georreferenciacion is True"
            )

    for key, value in updated_data.dict().items():
        setattr(localization, key, value)

    db.commit()
    db.refresh(localization)

    return localization