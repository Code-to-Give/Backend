from pydantic import BaseModel, Field, ConfigDict
from typing import Dict, Tuple
from uuid import UUID, uuid4


class Volunteer(BaseModel):
    name: str
    id: UUID = Field(default_factory=uuid4)
    location: Tuple[float, float] = (0.0, 0.0)
    capacity: int = 0
    delivery: int = 0

    model_config = ConfigDict(from_attributes=True)
