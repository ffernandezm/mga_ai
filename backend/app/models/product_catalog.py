import csv
import os
import logging

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import Column, Integer, String, Boolean, Text
from pydantic import BaseModel
from typing import List, Optional

from app.core.database import Base, SessionLocal

logger = logging.getLogger(__name__)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

FIELD_LABELS = {"sector_code": "Código del Sector",
                "sector_name": "Nombre del Sector",
                "program_code": "Código del Programa",
                "program_name": "Nombre del Programa",
                "product_code": "Código del Producto",
                "product_name": "Nombre del Producto",
                "description": "Descripción",
                "measured_through": "Medido a través de",
                "indicator_code": "Código del Indicador",
                "product_indicator": "Indicador de Producto",
                "measurement_unit": "Unidad de Medida",
                "main_indicator": "Indicador Principal",
                "is_national": "Es Nacional",
                "is_territorial": "Es Territorial",
                "selected_to_project": "Seleccionado para el Proyecto"}

# Modelo en SQLAlchemy
class ProductCatalog(Base):
    __tablename__ = "product_catalogs"
    __table_args__ = {
        "info": {
            "label_plural": "Catálogo de Productos",
            "label_singular": "Producto",
        }
    }

    id = Column(Integer, primary_key=True, index=True)
    sector_code = Column(Integer, info={"label": FIELD_LABELS["sector_code"]})
    sector_name = Column(String, info={"label": FIELD_LABELS["sector_name"]})
    program_code = Column(Integer, info={"label": FIELD_LABELS["program_code"]})
    program_name = Column(String, info={"label": FIELD_LABELS["program_name"]})
    product_code = Column(Integer, info={"label": FIELD_LABELS["product_code"]})
    product_name = Column(String, info={"label": FIELD_LABELS["product_name"]})
    description = Column(Text, info={"label": FIELD_LABELS["description"]})
    measured_through = Column(String, info={"label": FIELD_LABELS["measured_through"]})
    indicator_code = Column(Integer, info={"label": FIELD_LABELS["indicator_code"]})
    product_indicator = Column(String, info={"label": FIELD_LABELS["product_indicator"]})
    measurement_unit = Column(String, info={"label": FIELD_LABELS["measurement_unit"]})
    main_indicator = Column(String, info={"label": FIELD_LABELS["main_indicator"]})
    is_national = Column(String, info={"label": FIELD_LABELS["is_national"]})
    is_territorial = Column(String, info={"label": FIELD_LABELS["is_territorial"]})
    selected_to_project = Column(Boolean, default=False, info={"label": FIELD_LABELS["selected_to_project"]})


def seed_product_catalogs():
    """Carga los registros del CSV en la tabla product_catalogs si está vacía."""
    db = SessionLocal()
    try:
        count = db.query(ProductCatalog).count()
        if count > 0:
            logger.info(f"ProductCatalog ya tiene {count} registros, se omite la carga.")
            return

        csv_path = os.path.join(os.path.dirname(__file__), "..", "data", "products_catalog.csv")
        with open(csv_path, newline="", encoding="utf-8-sig") as csvfile:
            reader = csv.DictReader(csvfile, delimiter=";")
            records = []
            for row in reader:
                records.append(ProductCatalog(
                    sector_code=int(row["sector"]) if row.get("sector") else None,
                    sector_name=row.get("Nombre sector ", "").strip() or None,
                    program_code=int(row["Código programa"]) if row.get("Código programa") else None,
                    program_name=row.get("Programa", "").strip() or None,
                    product_code=int(row["Código Producto"]) if row.get("Código Producto") else None,
                    product_name=row.get("Producto", "").strip() or None,
                    description=row.get("Descripcion", "").strip() or None,
                    measured_through=row.get("Medido a través de", "").strip() or None,
                    indicator_code=int(row["codigo del indicador "]) if row.get("codigo del indicador ") else None,
                    product_indicator=row.get("Indicador de producto", "").strip() or None,
                    measurement_unit=row.get("Unidad de medida", "").strip() or None,
                    main_indicator=row.get("Indicador principal ", "").strip() or None,
                    is_national=row.get("Es Nacional", "").strip() or None,
                    is_territorial=row.get("Es Territorial", "").strip() or None,
                    selected_to_project=False,
                ))

        db.add_all(records)
        db.commit()
        logger.info(f"Se cargaron {len(records)} registros en ProductCatalog desde CSV.")
    except Exception as e:
        db.rollback()
        logger.error(f"Error al cargar ProductCatalog desde CSV: {e}", exc_info=True)
        raise
    finally:
        db.close()


# Esquemas Pydantic
class ProductCatalogBase(BaseModel):
    sector_code: Optional[int] = None
    sector_name: Optional[str] = None
    program_code: Optional[int] = None
    program_name: Optional[str] = None
    product_code: Optional[int] = None
    product_name: Optional[str] = None
    description: Optional[str] = None
    measured_through: Optional[str] = None
    indicator_code: Optional[int] = None
    product_indicator: Optional[str] = None
    measurement_unit: Optional[str] = None
    main_indicator: Optional[str] = None
    is_national: Optional[str] = None
    is_territorial: Optional[str] = None
    selected_to_project: Optional[bool] = False

class ProductCatalogResponse(ProductCatalogBase):
    id: int

    class Config:
        from_attributes = True

# Rutas de FastAPI
router = APIRouter()

# Obtener todos los product catalogs
@router.get("/", response_model=List[ProductCatalogResponse])
def get_product_catalogs(
    sector_code: Optional[int] = Query(None),
    program_code: Optional[int] = Query(None),
    db: Session = Depends(get_db),
):
    query = db.query(ProductCatalog)
    if sector_code is not None:
        query = query.filter(ProductCatalog.sector_code == sector_code)
    if program_code is not None:
        query = query.filter(ProductCatalog.program_code == program_code)
    return query.all()

# Obtener un product catalog por ID
@router.get("/{product_catalog_id}", response_model=ProductCatalogResponse)
def get_product_catalog(product_catalog_id: int, db: Session = Depends(get_db)):
    product_catalog = db.query(ProductCatalog).filter(ProductCatalog.id == product_catalog_id).first()
    if not product_catalog:
        raise HTTPException(status_code=404, detail="Product catalog not found")
    return product_catalog
