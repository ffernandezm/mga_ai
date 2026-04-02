from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, relationship
from sqlalchemy import Column, Integer, String, ForeignKey
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
class ProjectLocalization(Base):
    __tablename__ = "project_localizations"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    region = Column(String)
    department = Column(String)
    municipality = Column(String)

    # Relación con Project
    project = relationship("Project", back_populates="project_localizations")

# Esquemas Pydantic
class ProjectLocalizationBase(BaseModel):
    project_id: int
    region: Optional[str] = None
    department: Optional[str] = None
    municipality: Optional[str] = None

class ProjectLocalizationCreate(BaseModel):
    project_id: int
    region: Optional[str] = None
    department: Optional[str] = None
    municipality: Optional[str] = None

class ProjectLocalizationResponse(ProjectLocalizationBase):
    id: int

    class Config:
        from_attributes = True

# Rutas de FastAPI
router = APIRouter()

# Obtener todas las localizaciones por project_id
@router.get("/project/{project_id}", response_model=List[ProjectLocalizationResponse])
def get_project_localizations(project_id: int, db: Session = Depends(get_db)):
    return db.query(ProjectLocalization).filter(ProjectLocalization.project_id == project_id).all()

# Obtener una localización por ID
@router.get("/{localization_id}", response_model=ProjectLocalizationResponse)
def get_project_localization(localization_id: int, db: Session = Depends(get_db)):
    localization = db.query(ProjectLocalization).filter(ProjectLocalization.id == localization_id).first()
    if not localization:
        raise HTTPException(status_code=404, detail="Project localization not found")
    return localization

# Crear una nueva localización
@router.post("/", response_model=ProjectLocalizationResponse, status_code=201)
def create_project_localization(localization: ProjectLocalizationCreate, db: Session = Depends(get_db)):
    new_localization = ProjectLocalization(**localization.model_dump())
    db.add(new_localization)
    db.commit()
    db.refresh(new_localization)
    return new_localization

# Crear múltiples localizaciones
@router.post("/bulk", response_model=List[ProjectLocalizationResponse], status_code=201)
def create_project_localizations_bulk(localizations: List[ProjectLocalizationCreate], db: Session = Depends(get_db)):
    new_items = [ProjectLocalization(**loc.model_dump()) for loc in localizations]
    db.add_all(new_items)
    db.commit()
    for item in new_items:
        db.refresh(item)
    return new_items

# Actualizar una localización
@router.put("/{localization_id}", response_model=ProjectLocalizationResponse)
def update_project_localization(localization_id: int, localization: ProjectLocalizationCreate, db: Session = Depends(get_db)):
    db_localization = db.query(ProjectLocalization).filter(ProjectLocalization.id == localization_id).first()
    if not db_localization:
        raise HTTPException(status_code=404, detail="Project localization not found")
    for key, value in localization.model_dump().items():
        setattr(db_localization, key, value)
    db.commit()
    db.refresh(db_localization)
    return db_localization

# Eliminar una localización
@router.delete("/{localization_id}")
def delete_project_localization(localization_id: int, db: Session = Depends(get_db)):
    db_localization = db.query(ProjectLocalization).filter(ProjectLocalization.id == localization_id).first()
    if not db_localization:
        raise HTTPException(status_code=404, detail="Project localization not found")
    db.delete(db_localization)
    db.commit()
    return {"message": "Project localization deleted successfully"}

# Eliminar todas las localizaciones de un proyecto
@router.delete("/project/{project_id}")
def delete_project_localizations_by_project(project_id: int, db: Session = Depends(get_db)):
    deleted = db.query(ProjectLocalization).filter(ProjectLocalization.project_id == project_id).delete()
    db.commit()
    return {"message": f"{deleted} project localization(s) deleted successfully"}
