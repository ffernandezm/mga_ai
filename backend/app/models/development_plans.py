from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, relationship
from app.core.database import Base, SessionLocal
from sqlalchemy import Column, Integer, String, ForeignKey
from pydantic import BaseModel, ConfigDict
from typing import List, Optional

from app.models.pnd import (
    Pnd,
    PndCreate,
    PndResponse,
)

# ----------------------------
# Conexión a la DB
# ----------------------------
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ----------------------------
# Modelo SQLAlchemy
# ----------------------------
class DevelopmentPlans(Base):
    __tablename__ = "development_plans"

    id = Column(Integer, primary_key=True, index=True)
    # Contribución al Plan Nacional de Desarrollo
    program = Column(String, nullable=True)
    national_development_plan = Column(String, nullable=True)
    # Plan de Desarrollo Departamental o Sectorial
    departmental_or_sectoral_development_plan = Column(String, nullable=True)
    strategy_departmental = Column(String, nullable=True)
    program_departmental = Column(String, nullable=True)
    # Plan de Desarrollo Distrital o Municipal
    district_or_municipal_development_plan = Column(String, nullable=True)
    strategy_district = Column(String, nullable=True)
    program_district = Column(String, nullable=True)
    # Instrumentos de Planeación de Grupos Étnicos
    community_type = Column(String, nullable=True)
    ethnic_group_planning_instruments = Column(String, nullable=True)
    # Otros Instrumentos de Planeación
    other_development_plan = Column(String, nullable=True)
    strategy_other = Column(String, nullable=True)
    program_other = Column(String, nullable=True)

    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False, unique=True)
    project = relationship("Project", back_populates="development_plan")

    pnds = relationship(
        "Pnd",
        back_populates="development_plan",
        cascade="all, delete-orphan",
    )


# ----------------------------
# Esquemas Pydantic
# ----------------------------
class DevelopmentPlanBase(BaseModel):
    # Contribución al Plan Nacional de Desarrollo
    program: Optional[str] = None
    national_development_plan: Optional[str] = None
    # Plan de Desarrollo Departamental o Sectorial
    departmental_or_sectoral_development_plan: Optional[str] = None
    strategy_departmental: Optional[str] = None
    program_departmental: Optional[str] = None
    # Plan de Desarrollo Distrital o Municipal
    district_or_municipal_development_plan: Optional[str] = None
    strategy_district: Optional[str] = None
    program_district: Optional[str] = None
    # Instrumentos de Planeación de Grupos Étnicos
    community_type: Optional[str] = None
    ethnic_group_planning_instruments: Optional[str] = None
    # Otros Instrumentos de Planeación
    other_development_plan: Optional[str] = None
    strategy_other: Optional[str] = None
    program_other: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class DevelopmentPlanCreate(DevelopmentPlanBase):
    pnds: List[PndCreate] = []


class DevelopmentPlanUpdate(BaseModel):
    # Contribución al Plan Nacional de Desarrollo
    program: Optional[str] = None
    national_development_plan: Optional[str] = None
    # Plan de Desarrollo Departamental o Sectorial
    departmental_or_sectoral_development_plan: Optional[str] = None
    strategy_departmental: Optional[str] = None
    program_departmental: Optional[str] = None
    # Plan de Desarrollo Distrital o Municipal
    district_or_municipal_development_plan: Optional[str] = None
    strategy_district: Optional[str] = None
    program_district: Optional[str] = None
    # Instrumentos de Planeación de Grupos Étnicos
    community_type: Optional[str] = None
    ethnic_group_planning_instruments: Optional[str] = None
    # Otros Instrumentos de Planeación
    other_development_plan: Optional[str] = None
    strategy_other: Optional[str] = None
    program_other: Optional[str] = None
    pnds: Optional[List[PndCreate]] = None

    model_config = ConfigDict(from_attributes=True)


class DevelopmentPlanResponse(DevelopmentPlanBase):
    id: int
    project_id: int
    pnds: List[PndResponse] = []

    class Config:
        from_attributes = True  # ✅ Equivalente a orm_mode


# ----------------------------
# Rutas de FastAPI
# ----------------------------
router = APIRouter()


@router.post("/", response_model=DevelopmentPlanResponse)
def create_development_plan(plan: DevelopmentPlanCreate, db: Session = Depends(get_db)):
    plan_data = plan.dict()
    pnds_data = plan_data.pop('pnds', [])
    
    db_plan = DevelopmentPlans(**plan_data)
    db.add(db_plan)
    db.flush()  # Para obtener el id
    
    # Crear PNDs asociados
    for pnd_data in pnds_data:
        pnd_data['development_plan_id'] = db_plan.id
        db_pnd = Pnd(**pnd_data)
        db.add(db_pnd)
    
    db.commit()
    db.refresh(db_plan)
    return db_plan


@router.get("/", response_model=List[DevelopmentPlanResponse])
def get_development_plans(db: Session = Depends(get_db)):
    return db.query(DevelopmentPlans).all()


@router.get("/{project_id}", response_model=DevelopmentPlanResponse)
def get_development_plan(project_id: int, db: Session = Depends(get_db)):
    plan = db.query(DevelopmentPlans).filter(DevelopmentPlans.project_id == project_id).first()
    if not plan:
        raise HTTPException(status_code=404, detail="Development plan not found")
    return plan


@router.put("/{project_id}", response_model=DevelopmentPlanResponse)
def update_development_plan(project_id: int, updated: DevelopmentPlanUpdate, db: Session = Depends(get_db)):
    plan = db.query(DevelopmentPlans).filter(DevelopmentPlans.project_id == project_id).first()
    if not plan:
        raise HTTPException(status_code=404, detail="Development plan not found")

    updated_data = updated.dict(exclude_unset=True)
    pnds_data = updated_data.pop("pnds", None)

    for key, value in updated_data.items():
        setattr(plan, key, value)

    if pnds_data is not None:
        # Eliminar PNDs existentes y recrear
        for existing_pnd in plan.pnds:
            db.delete(existing_pnd)
        db.flush()
        for pnd_item in pnds_data:
            pnd_item["development_plan_id"] = plan.id
            db.add(Pnd(**pnd_item))

    db.commit()
    db.refresh(plan)
    return plan


@router.delete("/{project_id}")
def delete_development_plan(project_id: int, db: Session = Depends(get_db)):
    plan = db.query(DevelopmentPlans).filter(DevelopmentPlans.project_id == project_id).first()
    if not plan:
        raise HTTPException(status_code=404, detail="Development plan not found")

    db.delete(plan)
    db.commit()
    return {"message": "Development plan deleted successfully"}