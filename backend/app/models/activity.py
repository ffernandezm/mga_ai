from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, relationship
from sqlalchemy import Column, Integer, String, Float, ForeignKey, Text
from pydantic import BaseModel
from typing import List, Optional

from app.core.database import Base, SessionLocal

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Modelo en SQLAlchemy
class Activity(Base):
    __tablename__ = "activities"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    cost = Column(Float)
    stage = Column(String)
    description = Column(Text)

    # Relación con Project
    project = relationship("Project", back_populates="activities")

    # Relación con Product
    product = relationship("Product", back_populates="activities")

# Esquema Pydantic
class ActivityBase(BaseModel):
    project_id: int
    product_id: int
    cost: Optional[float] = None
    stage: Optional[str] = None
    description: Optional[str] = None

class ActivityCreate(BaseModel):
    project_id: int
    product_id: int
    cost: Optional[float] = None
    stage: Optional[str] = None
    description: Optional[str] = None

class ActivityResponse(ActivityBase):
    id: int

    class Config:
        from_attributes = True

# Rutas de FastAPI
router = APIRouter()

# Obtener todas las activities
@router.get("/", response_model=List[ActivityResponse])
def get_activities(db: Session = Depends(get_db)):
    activities = db.query(Activity).all()
    return activities

# Obtener una activity por ID
@router.get("/{activity_id}", response_model=ActivityResponse)
def get_activity(activity_id: int, db: Session = Depends(get_db)):
    activity = db.query(Activity).filter(Activity.id == activity_id).first()
    if not activity:
        raise HTTPException(status_code=404, detail="Activity not found")
    return activity

# Crear una nueva activity
@router.post("/", response_model=ActivityResponse, status_code=201)
def create_activity(activity: ActivityCreate, db: Session = Depends(get_db)):
    new_activity = Activity(**activity.model_dump())
    db.add(new_activity)
    db.commit()
    db.refresh(new_activity)
    return new_activity

# Actualizar una activity
@router.put("/{activity_id}", response_model=ActivityResponse)
def update_activity(activity_id: int, activity: ActivityCreate, db: Session = Depends(get_db)):
    db_activity = db.query(Activity).filter(Activity.id == activity_id).first()
    if not db_activity:
        raise HTTPException(status_code=404, detail="Activity not found")
    for key, value in activity.model_dump().items():
        setattr(db_activity, key, value)
    db.commit()
    db.refresh(db_activity)
    return db_activity

# Eliminar una activity
@router.delete("/{activity_id}")
def delete_activity(activity_id: int, db: Session = Depends(get_db)):
    db_activity = db.query(Activity).filter(Activity.id == activity_id).first()
    if not db_activity:
        raise HTTPException(status_code=404, detail="Activity not found")
    db.delete(db_activity)
    db.commit()
    return {"message": "Activity deleted successfully"}