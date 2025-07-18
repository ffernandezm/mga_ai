from sqlalchemy.orm import relationship
from sqlalchemy import Column, Integer, Text, ForeignKey
from pydantic import BaseModel
from app.core.database import Base

# Modelo SQLAlchemy para Efectos Indirectos
class IndirectCause(Base):
    __tablename__ = "indirect_causes"

    id = Column(Integer, primary_key=True, index=True)
    direct_cause_id = Column(Integer, ForeignKey("direct_causes.id", ondelete="CASCADE"))
    description = Column(Text)

    direct_cause = relationship("DirectCause", back_populates="indirect_causes")
    
# Esquemas Pydantic
class IndirectCauseBase(BaseModel):
    description: str

class IndirectCauseCreate(IndirectCauseBase):
    pass

class IndirectCauseResponse(IndirectCauseBase):
    id: int

    class Config:
        from_attributes = True
