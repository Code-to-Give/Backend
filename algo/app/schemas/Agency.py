# just for testing, should probably be a shared class with auth.
from pydantic import BaseModel, Field, ConfigDict
from schemas.FoodType import FoodType
from uuid import UUID, uuid4
from typing import Dict, Tuple

class Agency(BaseModel):
    name: str
    id: UUID = Field(default_factory=uuid4)
    priority_flag: bool = False
    location: Tuple[float, float] = (0.0, 0.0)
    
    model_config = ConfigDict(from_attributes=True)