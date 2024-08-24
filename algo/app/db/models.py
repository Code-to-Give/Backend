from sqlalchemy import Column, Integer, String, Enum as SqlEnum, JSON, ForeignKey, Boolean, Float
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from enum import Enum
from .database import Base

# Enums
class FoodType(str, Enum):
    HALAL = 'Halal'
    NON_HALAL = 'Non-Halal'
    VEGETARIAN = 'Vegetarian'
    VEGAN = 'Vegan'
    NON_BEEF = 'Non-Beef'

class DonationStatus(str, Enum):
    READY = 'Ready'
    ALLOCATED = 'Allocated'
    ACCEPTED = 'Accepted'
    COLLECTED = 'Collected'

# Entity models
class AgencyModel(Base):
    __tablename__ = "agencies"

    id = Column(String, primary_key=True, index=True)
    name = Column(String, nullable=False)
    requirements = Column(JSON, nullable=False)
    priority_flag = Column(Boolean, default=False)
    location = Column(JSON, nullable=False, default=lambda: [0.0, 0.0])
 
    def __repr__(self):
        return f"<Agency(id={self.id}, name={self.name})>"

class DonationModel(Base):
    __tablename__ = "donations"

    id = Column(String, primary_key=True, index=True)
    donor_id = Column(String, ForeignKey("donors.id"), nullable=False)
    items = Column(JSON, nullable=False)
    location = Column(JSON, nullable=False, default=lambda: [0.0, 0.0])
    status = Column(SqlEnum(DonationStatus), default=DonationStatus.READY)
    agency_id = Column(String, default="")

    def __repr__(self):
        return f"<Donation(id={self.id}, donor_id={self.donor_id}, status={self.status})>"

class DonorModel(Base):
    __tablename__ = "donors"

    id = Column(String, primary_key=True, index=True)
    name = Column(String, nullable=False)
    location = Column(JSON, nullable=False, default=lambda: [0.0, 0.0])
    donations = Column(Float, nullable=True)  # Assuming this represents total donation weight

    def __repr__(self):
        return f"<Donor(id={self.id}, name={self.name})>"
