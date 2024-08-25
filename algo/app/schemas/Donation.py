from pydantic import BaseModel, Field, ConfigDict
from schemas.FoodType import FoodType
from schemas.DonationStatus import DonationStatus
from uuid import UUID, uuid4
from typing import Dict, Tuple, Optional
from datetime import datetime

class Donation(BaseModel):
    donor_id: UUID
    food_type: str
    quantity: int
    id: UUID = Field(default_factory=uuid4)
    location: Tuple[float, float] = (0.0, 0.0)
    status: str = DonationStatus.READY
    agency_id: Optional[UUID] = None
    expiry_time: datetime = Field(default_factory=datetime.utcnow)

    model_config = ConfigDict(from_attributes=True)


class DonationCreated(BaseModel):
    food_type: str
    quantity: int
    location: Tuple[float, float] = (0.0, 0.0)
    status: str = DonationStatus.READY
    expiry_time: datetime = Field(default_factory=datetime.utcnow)
