from sqlalchemy.orm import relationship
from sqlalchemy import Column, Integer, Text, ForeignKey
from pydantic import BaseModel
from app.core.database import Base
from typing import List

from app.models.indirect_causes import IndirectCauseCreate, IndirectCauseResponse


# Modelo SQLAlchemy para Efectos
class DirectCause(Base):
    __tablename__ = "direct_causes"

    id = Column(Integer, primary_key=True, index=True)
    problem_id = Column(Integer, ForeignKey("problems.id", ondelete="CASCADE"))
    description = Column(Text)
    problem = relationship("Problem", back_populates="direct_causes")
    
    # Relaciones
    indirect_causes = relationship("IndirectCause", back_populates="direct_cause")
    
# Esquemas Pydantic
class DirectCauseBase(BaseModel):
    description: str

class DirectCauseCreate(DirectCauseBase):
    indirect_causes: List[IndirectCauseCreate] = []
    

class DirectCauseResponse(DirectCauseBase):
    id: int
    indirect_causes: List[IndirectCauseResponse] = []

    class Config:
        from_attributes = True
