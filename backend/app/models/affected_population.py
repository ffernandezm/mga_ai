from fastapi import APIRouter, Depends
from sqlalchemy.orm import relationship
from sqlalchemy import Column, Integer, Text, ForeignKey
from pydantic import BaseModel
from app.core.database import Base

# Modelo SQLAlchemy para Efectos Indirectos
class AffectedPopulation(Base):
    __tablename__ = "affected_population"

    id = Column(Integer, primary_key=True, index=True)
    direct_effect_id = Column(Integer, ForeignKey("direct_effects.id", ondelete="CASCADE"))
    description = Column(Text)

    participants_general_id = Column(Integer, ForeignKey("participants_general.id"), nullable=False)
    #participants_general = relationship("Population", back_populates="affected_population")


# Esquemas Pydantic
class AffectedPopulationBase(BaseModel):
    description: str

class AffectedPopulationCreate(AffectedPopulation):
    participants_general_id: int

class AffectedPopulationResponse(AffectedPopulation):
    id: int
    
    participants_general_id: int

    class Config:
        from_attributes = True

# Rutas de FastAPI
router = APIRouter()
