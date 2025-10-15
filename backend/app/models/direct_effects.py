from sqlalchemy.orm import relationship
from sqlalchemy import Column, Integer, Text, ForeignKey
from pydantic import BaseModel
from app.core.database import Base
from typing import List

from app.models.indirect_effects import IndirectEffectResponse, IndirectEffectCreate


# Modelo SQLAlchemy para Efectos
class DirectEffect(Base):
    __tablename__ = "direct_effects"

    id = Column(Integer, primary_key=True, index=True)
    problem_id = Column(Integer, ForeignKey("problems.id", ondelete="CASCADE"))
    description = Column(Text)
    problem = relationship("Problems", back_populates="direct_effects")

    # Relaciones
    indirect_effects = relationship("IndirectEffect", back_populates="direct_effect")
    
    
    
# Esquemas Pydantic
class DirectEffectBase(BaseModel):
    description: str

class DirectEffectCreate(DirectEffectBase):
    indirect_effects: List[IndirectEffectCreate] = []


class DirectEffectResponse(DirectEffectBase):
    id: int
    indirect_effects: List[IndirectEffectResponse] = []

    class Config:
        from_attributes = True