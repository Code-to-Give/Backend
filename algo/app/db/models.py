from sqlalchemy import Column, Integer, String, Enum as SqlEnum, JSON, ForeignKey, Boolean, Float, DateTime, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.ext.declarative import declarative_base
from enum import Enum
import uuid
from .database import Base

# Enums


class FoodType(str, Enum):
    HALAL = 'halal'
    NONE = 'none'
    VEGETARIAN = 'vegetarian'
    NON_BEEF = 'no-beef'


class DonationStatus(str, Enum):
    READY = 'Ready'
    ALLOCATED = 'Allocated'
    ACCEPTED = 'Accepted'
    COLLECTED = 'Collected'

# Entity models


class AgencyModel(Base):
    __tablename__ = "agencies"

    id = Column(UUID(as_uuid=True), primary_key=True,
                index=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    priority_flag = Column(Boolean, default=False)
    location = Column(JSON, nullable=False, default=lambda: [0.0, 0.0])

    def __repr__(self):
        return f"<Agency(id={self.id}, name={self.name})>"


class DonationModel(Base):
    __tablename__ = "donations"

    id = Column(UUID(as_uuid=True), primary_key=True, index=True)
    donor_id = Column(UUID(as_uuid=True), ForeignKey(
        "donors.id"), nullable=False)
    # Represents a specific type of food
    food_type = Column(SqlEnum(FoodType), nullable=False)
    # Represents the quantity of the food type
    quantity = Column(Integer, nullable=False)
    location = Column(JSON, nullable=False, default=lambda: [0.0, 0.0])
    status = Column(SqlEnum(DonationStatus), default=DonationStatus.READY)
    agency_id = Column(UUID(as_uuid=True), ForeignKey(
        "agencies.id"), nullable=True)
    expiry_time = Column(DateTime(timezone=True), server_default=func.now())

    def __repr__(self):
        return f"<Donation(id={self.id}, donor_id={self.donor_id}, status={self.status})>"


class DonorModel(Base):
    __tablename__ = "donors"

    id = Column(UUID(as_uuid=True), primary_key=True, index=True)
    name = Column(String, nullable=False)
    location = Column(JSON, nullable=False, default=lambda: [0.0, 0.0])
    # Assuming this represents total donation weight
    donations = Column(Float, nullable=True)

    def __repr__(self):
        return f"<Donor(id={self.id}, name={self.name})>"


class RequirementModel(Base):
    __tablename__ = "requirements"

    id = Column(UUID(as_uuid=True), primary_key=True, index=True)
    agency_id = Column(UUID(as_uuid=True), ForeignKey(
        'agencies.id'), nullable=False)
    food_type = Column(SqlEnum(FoodType), nullable=False)
    quantity = Column(Integer, nullable=False)

    __table_args__ = (
        UniqueConstraint('agency_id', 'food_type', name='uq_agency_food_type'),
    )
