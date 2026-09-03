from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, Field


class SectionStatus(str, Enum):
    NOT_STARTED = "NOT_STARTED"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETE = "COMPLETE"
    BLOCKED = "BLOCKED"


class MissingField(BaseModel):
    key: str
    label: str
    path: str
    message: str = "Este campo es obligatorio."


class BlockingRule(BaseModel):
    key: str
    message: str


class ConsistencyFinding(BaseModel):
    severity: str
    section: str
    related_section: Optional[str] = None
    description: str


class SectionValidationResult(BaseModel):
    section: str
    status: SectionStatus
    complete: bool
    missing_fields: List[MissingField] = Field(default_factory=list)
    blocking_rules: List[BlockingRule] = Field(default_factory=list)
    prerequisites_complete: bool = True
    incomplete_prerequisites: List[str] = Field(default_factory=list)
    completion_percent: int = 0
    required_fields_completed: int = 0
    required_fields_total: int = 0
    warnings: List[str] = Field(default_factory=list)


class ProjectReviewResult(BaseModel):
    status: str
    sections: List[SectionValidationResult]
    findings: List[ConsistencyFinding] = Field(default_factory=list)