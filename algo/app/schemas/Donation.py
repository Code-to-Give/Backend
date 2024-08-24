from pydantic.dataclasses import dataclass, Field
from pydantic import BaseModel
from schemas.FoodType import FoodType
from schemas.DonationStatus import DonationStatus
from uuid import UUID, uuid4
from typing import Dict, Tuple, Optional

@dataclass
class Donation:
    donor_id: str
    id: str = Field(default_factory=lambda: str(uuid4()))
    items: Dict[FoodType, int] = Field(default_factory=dict)
    location: Tuple[float, float] = (0.0, 0.0)
    status: DonationStatus = DonationStatus.READY
    agency_id: Optional[int] = None
    