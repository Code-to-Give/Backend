from pydantic import BaseModel, Field, ConfigDict
from typing import Dict, Tuple
from uuid import UUID, uuid4


class Donor(BaseModel):
    name: str
    id: UUID = Field(default_factory=uuid4)
    location: Tuple[float, float] = (0.0, 0.0)
    # in weight i suppose? subject to changes idk what the frontend is planning to put on dashboard
    donations: float = 0.0

    model_config = ConfigDict(from_attributes=True)


class DonorLocationUpdate(BaseModel):
    location: Tuple[float, float]


class DonorDonationsUpdate(BaseModel):
    donations: float
