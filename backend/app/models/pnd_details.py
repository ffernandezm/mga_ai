import csv
import logging
import os
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy import Boolean, Column, Integer, String, Text
from sqlalchemy.orm import Session

from app.core.database import Base, SessionLocal

logger = logging.getLogger(__name__)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


class PndDetail(Base):
    __tablename__ = "pnd_details"

    id = Column(Integer, primary_key=True, index=True)
    source_id = Column(Integer)
    plan_id = Column(Integer)
    plan_name = Column(String)
    pillar_id = Column(Integer)
    objective_id = Column(Integer)
    strategy_id = Column(Integer)
    component_id = Column(Integer)
    pillar_description = Column(Text)
    objective_description = Column(Text)
    strategy_description = Column(Text)
    component_description = Column(Text)
    row_state = Column(Integer)
    unique_identifier = Column(String)
    selected_to_project = Column(Boolean, default=False)


def _to_int(value: Optional[str]) -> Optional[int]:
    if value is None:
        return None
    value = value.strip()
    if not value:
        return None
    return int(value)


def seed_pnd_details():
    """Carga los registros del CSV en la tabla pnd_details si está vacía."""
    db = SessionLocal()
    try:
        count = db.query(PndDetail).count()
        if count > 0:
            logger.info(f"PndDetail ya tiene {count} registros, se omite la carga.")
            return

        csv_path = os.path.join(os.path.dirname(__file__), "..", "data", "pnd_details.csv")
        with open(csv_path, newline="", encoding="utf-8-sig") as csvfile:
            reader = csv.DictReader(csvfile)
            records = []
            for row in reader:
                records.append(
                    PndDetail(
                        source_id=_to_int(row.get("Id")),
                        plan_id=_to_int(row.get("PlanId")),
                        plan_name=row.get("PlanName", "").strip() or None,
                        pillar_id=_to_int(row.get("PillarId")),
                        objective_id=_to_int(row.get("ObjectiveId")),
                        strategy_id=_to_int(row.get("StrategyId")),
                        component_id=_to_int(row.get("ComponentId")),
                        pillar_description=row.get("PillarDescription", "").strip() or None,
                        objective_description=row.get("ObjectiveDescription", "").strip() or None,
                        strategy_description=row.get("StrategyDescription", "").strip() or None,
                        component_description=row.get("ComponentDescription", "").strip() or None,
                        row_state=_to_int(row.get("RowState")),
                        unique_identifier=row.get("UniqueIdentifier", "").strip() or None,
                        selected_to_project=False,
                    )
                )

        db.add_all(records)
        db.commit()
        logger.info(f"Se cargaron {len(records)} registros en PndDetail desde CSV.")
    except Exception as e:
        db.rollback()
        logger.error(f"Error al cargar PndDetail desde CSV: {e}", exc_info=True)
        raise
    finally:
        db.close()


class PndDetailBase(BaseModel):
    source_id: Optional[int] = None
    plan_id: Optional[int] = None
    plan_name: Optional[str] = None
    pillar_id: Optional[int] = None
    objective_id: Optional[int] = None
    strategy_id: Optional[int] = None
    component_id: Optional[int] = None
    pillar_description: Optional[str] = None
    objective_description: Optional[str] = None
    strategy_description: Optional[str] = None
    component_description: Optional[str] = None
    row_state: Optional[int] = None
    unique_identifier: Optional[str] = None
    selected_to_project: Optional[bool] = False


class PndDetailResponse(PndDetailBase):
    id: int

    class Config:
        from_attributes = True


router = APIRouter()


@router.get("/", response_model=List[PndDetailResponse])
def get_pnd_details(
    plan_id: Optional[int] = Query(None),
    pillar_id: Optional[int] = Query(None),
    objective_id: Optional[int] = Query(None),
    strategy_id: Optional[int] = Query(None),
    db: Session = Depends(get_db),
):
    query = db.query(PndDetail)
    if plan_id is not None:
        query = query.filter(PndDetail.plan_id == plan_id)
    if pillar_id is not None:
        query = query.filter(PndDetail.pillar_id == pillar_id)
    if objective_id is not None:
        query = query.filter(PndDetail.objective_id == objective_id)
    if strategy_id is not None:
        query = query.filter(PndDetail.strategy_id == strategy_id)
    return query.all()


@router.get("/{pnd_detail_id}", response_model=PndDetailResponse)
def get_pnd_detail(pnd_detail_id: int, db: Session = Depends(get_db)):
    pnd_detail = db.query(PndDetail).filter(PndDetail.id == pnd_detail_id).first()
    if not pnd_detail:
        raise HTTPException(status_code=404, detail="PND detail not found")
    return pnd_detail