from enum import Enum
from pydantic import BaseModel, Field, ConfigDict
from uuid import UUID, uuid4
from typing import List


class Requirement(BaseModel):
    agency_id: UUID
    quantity: int
    food_type: str
    id: UUID = Field(default_factory=uuid4)

    model_config = ConfigDict(from_attributes=True)


class RequirementCreated(BaseModel):
    quantity: int
    food_type: str

    model_config = ConfigDict(from_attributes=True)
