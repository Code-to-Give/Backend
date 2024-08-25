from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from db.database import get_db
from db.models import DonationModel, AgencyModel
from schemas.Donation import Donation, DonationCreated
from schemas.Agency import Agency
from schemas.DonationStatus import DonationStatus
from AllocationSystem import AllocationSystem
from routers.agency_router import read_agencies
from typing import List, Tuple
from AllocationSystem import get_allocation_system
from pydantic import BaseModel
from uuid import UUID

from utils.jwt_auth import get_current_user

router = APIRouter()


class AgencyUpdate(BaseModel):
    agency_id: UUID


class DonationStatusUpdate(BaseModel):
    status: DonationStatus

# Temporary function for non-routed reads


async def fetch_agencies(db: AsyncSession, skip: int = 0, limit: int = 100):
    result = await db.execute(select(AgencyModel).offset(skip).limit(limit))
    agencies = result.scalars().all()
    return [Agency.model_validate(agency) for agency in agencies]


@router.post("/donations", response_model=Donation)
async def create_donation(
    donation_created: DonationCreated,
    db: AsyncSession = Depends(get_db),
    allocation_system: AllocationSystem = Depends(get_allocation_system),
    current_user=Depends(get_current_user)
):
    donation = Donation(
        donor_id=current_user["sub"],
        food_type=donation_created.food_type,
        quantity=donation_created.quantity,
        location=donation_created.location,
        status=donation_created.status,
        expiry_time=donation_created.expiry_time
    )

    db_donation = DonationModel(**donation.model_dump())
    db.add(db_donation)
    await db.commit()
    await db.refresh(db_donation)

    # # Trigger the allocation process for the new donation
    agencies = await fetch_agencies(db)
    await allocation_system.allocate_donation(donation, agencies)

    return Donation.model_validate(db_donation)


@router.get("/donations", response_model=List[Donation])
async def read_donations(skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(DonationModel).offset(skip).limit(limit))
    donations = result.scalars().all()
    return [Donation.model_validate(donation) for donation in donations]


@router.get("/donations/{donation_id}", response_model=Donation)
async def read_donation(donation_id: UUID, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(DonationModel).filter(DonationModel.id == donation_id))
    donation = result.scalar_one_or_none()
    if donation is None:
        raise HTTPException(status_code=404, detail="Donation not found")
    return Donation.model_validate(donation)


@router.put("/donations/{donation_id}", response_model=Donation)
async def update_donation(donation_id: UUID, donation: Donation, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(DonationModel).filter(DonationModel.id == donation_id))
    db_donation = result.scalar_one_or_none()
    if db_donation is None:
        raise HTTPException(status_code=404, detail="Donation not found")

    for key, value in donation.dict(exclude_unset=True).items():
        setattr(db_donation, key, value)

    await db.commit()
    await db.refresh(db_donation)
    return Donation.model_validate(db_donation)


@router.delete("/donations/{donation_id}", response_model=Donation)
async def delete_donation(donation_id: UUID, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(DonationModel).filter(DonationModel.id == donation_id))
    donation = result.scalar_one_or_none()
    if donation is None:
        raise HTTPException(status_code=404, detail="Donation not found")
    await db.delete(donation)
    await db.commit()
    return Donation.model_validate(donation)


@router.patch("/donations/{donation_id}/status", response_model=Donation)
async def update_donation_status(donation_id: UUID, status: DonationStatus, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(DonationModel).filter(DonationModel.id == donation_id))
    donation = result.scalar_one_or_none()
    if donation is None:
        raise HTTPException(status_code=404, detail="Donation not found")
    donation.status = status
    await db.commit()
    await db.refresh(donation)
    return Donation.model_validate(donation)


@router.patch("/donations/{donation_id}/agency", response_model=Donation)
async def update_donation_agency(donation_id: UUID, update_data: AgencyUpdate, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(DonationModel).filter(DonationModel.id == donation_id))
    donation = result.scalar_one_or_none()
    if donation is None:
        raise HTTPException(status_code=404, detail="Donation not found")
    donation.agency_id = update_data.agency_id
    await db.commit()
    await db.refresh(donation)
    return Donation.model_validate(donation)


@router.patch("/donations/{donation_id}/location", response_model=Donation)
async def update_donation_location(donation_id: UUID, location: Tuple[float, float], db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(DonationModel).filter(DonationModel.id == donation_id))
    donation = result.scalar_one_or_none()
    if donation is None:
        raise HTTPException(status_code=404, detail="Donation not found")
    donation.location = location
    await db.commit()
    await db.refresh(donation)
    return Donation.model_validate(donation)
