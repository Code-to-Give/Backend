from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from db.database import get_db
from db.models import VolunteerModel, DonationModel
from schemas.Volunteer import Volunteer, VolunteerLocationUpdate
from schemas.Donation import Donation
from typing import List, Tuple
from uuid import UUID
from utils.jwt_auth import get_current_user
from pydantic import BaseModel

router = APIRouter()

class VolunteerCapacityUpdate(BaseModel):
    capacity: int

class VolunteerDeliveryUpdate(BaseModel):
    delivery: int

@router.post("/volunteers", response_model=Volunteer)
async def create_volunteer(
        db: AsyncSession = Depends(get_db),
        current_user=Depends(get_current_user)):

    if current_user["role"] != "Volunteer":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authorized to create a volunteer."
        )

    # Check if a volunteer with this name already exists
    result = await db.execute(select(VolunteerModel).filter_by(name=current_user["name"]))
    existing_volunteer = result.scalars().first()

    # If it exists, return the existing volunteer
    if existing_volunteer:
        return existing_volunteer

    # If it doesn't exist, create a new volunteer
    volunteer = Volunteer(
        name=current_user["name"]
    )

    db_volunteer = VolunteerModel(**volunteer.model_dump())
    db.add(db_volunteer)
    await db.commit()
    await db.refresh(db_volunteer)
    return Volunteer.model_validate(db_volunteer)

@router.get("/volunteers", response_model=List[Volunteer])
async def read_volunteers(skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(VolunteerModel).offset(skip).limit(limit))
    volunteers = result.scalars().all()
    return [Volunteer.model_validate(volunteer) for volunteer in volunteers]

@router.get("/volunteers/{volunteer_id}", response_model=Volunteer)
async def read_volunteer(volunteer_id: UUID, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(VolunteerModel).filter(VolunteerModel.id == volunteer_id))
    volunteer = result.scalar_one_or_none()
    if volunteer is None:
        raise HTTPException(status_code=404, detail="Volunteer not found")
    return Volunteer.model_validate(volunteer)

@router.put("/volunteers/{volunteer_id}", response_model=Volunteer)
async def update_volunteer(volunteer_id: UUID, volunteer: Volunteer, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(VolunteerModel).filter(VolunteerModel.id == volunteer_id))
    db_volunteer = result.scalar_one_or_none()
    if db_volunteer is None:
        raise HTTPException(status_code=404, detail="Volunteer not found")
    
    for key, value in volunteer.dict(exclude_unset=True).items():
        setattr(db_volunteer, key, value)
    
    await db.commit()
    await db.refresh(db_volunteer)
    return Volunteer.model_validate(db_volunteer)

@router.delete("/volunteers/{volunteer_id}", response_model=Volunteer)
async def delete_volunteer(volunteer_id: UUID, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(VolunteerModel).filter(VolunteerModel.id == volunteer_id))
    volunteer = result.scalar_one_or_none()
    if volunteer is None:
        raise HTTPException(status_code=404, detail="Volunteer not found")
    await db.delete(volunteer)
    await db.commit()
    return Volunteer.model_validate(volunteer)


@router.patch("/volunteers/{volunteer_id}/location", response_model=Volunteer)
async def update_volunteer_location(volunteer_id: UUID, location_update: VolunteerLocationUpdate, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(VolunteerModel).filter(VolunteerModel.id == volunteer_id))
    volunteer = result.scalar_one_or_none()
    if volunteer is None:
        raise HTTPException(status_code=404, detail="Volunteer not found")
    volunteer.location = location_update.location
    await db.commit()
    await db.refresh(volunteer)
    return Volunteer.model_validate(volunteer)

@router.patch("/volunteers/{volunteer_id}/capacity", response_model=Volunteer)
async def update_volunteer_capacity(volunteer_id: UUID, capacity_update: VolunteerCapacityUpdate, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(VolunteerModel).filter(VolunteerModel.id == volunteer_id))
    volunteer = result.scalar_one_or_none()
    if volunteer is None:
        raise HTTPException(status_code=404, detail="Volunteer not found")
    volunteer.capacity = capacity_update.capacity
    await db.commit()
    await db.refresh(volunteer)
    return Volunteer.model_validate(volunteer)

@router.patch("/volunteers/{volunteer_id}/delivery", response_model=Volunteer)
async def update_volunteer_delivery(volunteer_id: UUID, delivery_update: VolunteerDeliveryUpdate, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(VolunteerModel).filter(VolunteerModel.id == volunteer_id))
    volunteer = result.scalar_one_or_none()
    if volunteer is None:
        raise HTTPException(status_code=404, detail="Volunteer not found")
    volunteer.delivery = delivery_update.delivery
    await db.commit()
    await db.refresh(volunteer)
    return Volunteer.model_validate(volunteer)

@router.get("/volunteers/{volunteer_id}/donations", response_model=List[Donation])
async def read_donations_by_volunteer(volunteer_id: UUID, db: AsyncSession = Depends(get_db)):
    # First, check if the volunteer exists
    volunteer_result = await db.execute(select(VolunteerModel).filter(VolunteerModel.id == volunteer_id))
    volunteer = volunteer_result.scalar_one_or_none()
    if volunteer is None:
        raise HTTPException(status_code=404, detail="Volunteer not found")

    # Then, fetch all donations associated with this volunteer
    result = await db.execute(select(DonationModel).filter(DonationModel.volunteer_id == volunteer_id))
    donations = result.scalars().all()
    
    return [Donation.model_validate(donation) for donation in donations]