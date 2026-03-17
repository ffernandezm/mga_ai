from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, relationship
from app.core.database import Base, SessionLocal
from sqlalchemy import Column, Integer, String, ForeignKey
from pydantic import BaseModel, ConfigDict
from typing import List, Optional

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
class Pnd(Base):
    __tablename__ = "pnds"

    id = Column(Integer, primary_key=True, index=True)
    transformation = Column(String, nullable=True)
    pillar = Column(String, nullable=True)
    catalyst = Column(String, nullable=True)
    component = Column(String, nullable=True)

    development_plan_id = Column(Integer, ForeignKey("development_plans.id"), nullable=False)
    development_plan = relationship("DevelopmentPlan", back_populates="pnds")


# ----------------------------
# Esquemas Pydantic
# ----------------------------
class PndBase(BaseModel):
    transformation: Optional[str] = None
    pillar: Optional[str] = None
    catalyst: Optional[str] = None
    component: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class PndCreate(PndBase):
    pass


class PndUpdate(BaseModel):
    transformation: Optional[str] = None
    pillar: Optional[str] = None
    catalyst: Optional[str] = None
    component: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class PndResponse(PndBase):
    id: int
    development_plan_id: int

    class Config:
        from_attributes = True  # ✅ Equivalente a orm_mode


# ----------------------------
# Rutas de FastAPI
# ----------------------------
router = APIRouter()


@router.post("/", response_model=PndResponse)
def create_pnd(pnd: PndCreate, db: Session = Depends(get_db)):
    db_pnd = Pnd(**pnd.dict())
    db.add(db_pnd)
    db.commit()
    db.refresh(db_pnd)
    return db_pnd


@router.get("/", response_model=List[PndResponse])
def get_pnds(db: Session = Depends(get_db)):
    return db.query(Pnd).all()


@router.get("/{pnd_id}", response_model=PndResponse)
def get_pnd(pnd_id: int, db: Session = Depends(get_db)):
    pnd = db.query(Pnd).filter(Pnd.id == pnd_id).first()
    if not pnd:
        raise HTTPException(status_code=404, detail="PND not found")
    return pnd


@router.put("/{pnd_id}", response_model=PndResponse)
def update_pnd(pnd_id: int, updated: PndUpdate, db: Session = Depends(get_db)):
    pnd = db.query(Pnd).filter(Pnd.id == pnd_id).first()
    if not pnd:
        raise HTTPException(status_code=404, detail="PND not found")

    updated_data = updated.dict(exclude_unset=True)
    for key, value in updated_data.items():
        setattr(pnd, key, value)

    db.commit()
    db.refresh(pnd)
    return pnd


@router.delete("/{pnd_id}")
def delete_pnd(pnd_id: int, db: Session = Depends(get_db)):
    pnd = db.query(Pnd).filter(Pnd.id == pnd_id).first()
    if not pnd:
        raise HTTPException(status_code=404, detail="PND not found")

    db.delete(pnd)
    db.commit()
    return {"message": "PND deleted successfully"}