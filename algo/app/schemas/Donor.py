from pydantic import BaseModel, Field, ConfigDict
from typing import Dict, Tuple
import uuid

class Donor(BaseModel):
    name: str
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    location: Tuple[float, float] = (0.0, 0.0)
    donations: float = 0.0 #in weight i suppose? subject to changes idk what the frontend is planning to put on dashboard
    
    model_config = ConfigDict(from_attributes=True)