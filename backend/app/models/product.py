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
class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    value_chain_objective_id = Column(Integer, ForeignKey("value_chain_objectives.id"), nullable=False)
    measured_through = Column(String)
    quantity = Column(Float)
    cost = Column(Float)
    stage = Column(String)
    description = Column(Text)

    # Relación con Project
    project = relationship("Project", back_populates="products")

    # Relación con ValueChainObjectives
    value_chain_objective = relationship("ValueChainObjectives", back_populates="products")

    # Relación con Activities
    activities = relationship(
        "Activity",
        back_populates="product",
        cascade="all, delete-orphan"
    )

# Esquema Pydantic
class ProductBase(BaseModel):
    project_id: int
    value_chain_objective_id: int
    measured_through: Optional[str] = None
    quantity: Optional[float] = None
    cost: Optional[float] = None
    stage: Optional[str] = None
    description: Optional[str] = None

class ProductCreate(BaseModel):
    project_id: int
    value_chain_objective_id: int
    measured_through: Optional[str] = None
    quantity: Optional[float] = None
    cost: Optional[float] = None
    stage: Optional[str] = None
    description: Optional[str] = None

class ProductResponse(ProductBase):
    id: int

    class Config:
        from_attributes = True

# Rutas de FastAPI
router = APIRouter()

# Obtener todos los products
@router.get("/", response_model=List[ProductResponse])
def get_products(db: Session = Depends(get_db)):
    products = db.query(Product).all()
    return products

# Obtener un product por ID
@router.get("/{product_id}", response_model=ProductResponse)
def get_product(product_id: int, db: Session = Depends(get_db)):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product

# Crear un nuevo product
@router.post("/", response_model=ProductResponse, status_code=201)
def create_product(product: ProductCreate, db: Session = Depends(get_db)):
    new_product = Product(**product.model_dump())
    db.add(new_product)
    db.commit()
    db.refresh(new_product)
    return new_product

# Actualizar un product
@router.put("/{product_id}", response_model=ProductResponse)
def update_product(product_id: int, product: ProductCreate, db: Session = Depends(get_db)):
    db_product = db.query(Product).filter(Product.id == product_id).first()
    if not db_product:
        raise HTTPException(status_code=404, detail="Product not found")
    for key, value in product.model_dump().items():
        setattr(db_product, key, value)
    db.commit()
    db.refresh(db_product)
    return db_product

# Eliminar un product
@router.delete("/{product_id}")
def delete_product(product_id: int, db: Session = Depends(get_db)):
    db_product = db.query(Product).filter(Product.id == product_id).first()
    if not db_product:
        raise HTTPException(status_code=404, detail="Product not found")
    db.delete(db_product)
    db.commit()
    return {"message": "Product deleted successfully"}