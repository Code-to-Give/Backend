from pydantic import BaseModel, Field, ConfigDict
from uuid import UUID, uuid4
from typing import Tuple

class Volunteer(BaseModel):
    capacity = int
    id: UUID = Field(default_factory=uuid4)
    location: Tuple[float, float] = (0.0, 0.0)

    model_config = ConfigDict(from_attributes=True)
