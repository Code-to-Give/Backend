# just for testing, should probably be a shared class with auth.
from pydantic.dataclasses import dataclass, Field
from schemas.FoodType import FoodType
from uuid import UUID, uuid4
from typing import Dict, Tuple

@dataclass
class Agency:
    name: str
    id: str = Field(default_factory=lambda: str(uuid4()))
    requirements: Dict[FoodType, int] = Field(default_factory=dict)
    priority_flag: bool = False
    location: Tuple[float, float] = (0.0, 0.0)