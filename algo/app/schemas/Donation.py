from pydantic import BaseModel, Field, ConfigDict
from schemas.FoodType import FoodType
from schemas.DonationStatus import DonationStatus
from uuid import UUID, uuid4
from typing import Dict, Tuple, Optional

class Donation(BaseModel):
    donor_id: str
    id: str = Field(default_factory=lambda: str(uuid4()))
    items: Dict[str, int] = Field(default_factory=dict)
    location: Tuple[float, float] = (0.0, 0.0)
    status: str = DonationStatus.READY
    agency_id: str = ""
    
    model_config = ConfigDict(from_attributes=True)
    