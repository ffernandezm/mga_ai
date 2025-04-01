from sqlalchemy.orm import relationship
from sqlalchemy import Column, Integer, Text, ForeignKey
from pydantic import BaseModel
from app.core.database import Base

# Modelo SQLAlchemy para Efectos Indirectos
class IndirectEffect(Base):
    __tablename__ = "indirect_effects"

    id = Column(Integer, primary_key=True, index=True)
    direct_effect_id = Column(Integer, ForeignKey("direct_effects.id", ondelete="CASCADE"))
    description = Column(Text)

    direct_effect = relationship("DirectEffect", back_populates="indirect_effects")
    
# Esquemas Pydantic
class IndirectEffectBase(BaseModel):
    description: str

class IndirectEffectCreate(IndirectEffectBase):
    pass

class IndirectEffectResponse(IndirectEffectBase):
    id: int

    class Config:
        from_attributes = True
