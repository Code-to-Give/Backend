from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from db.database import get_db
from db.models import DonationModel
from schemas.Donation import Donation
from schemas.DonationStatus import DonationStatus
from typing import List, Tuple

router = APIRouter()

@router.post("/donations", response_model=Donation)
async def create_donation(donation: Donation, db: AsyncSession = Depends(get_db)):
    db_donation = DonationModel(**donation.model_dump())
    db.add(db_donation)
    await db.commit()
    await db.refresh(db_donation)
    return Donation.model_validate(db_donation)

@router.get("/donations", response_model=List[Donation])
async def read_donations(skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(DonationModel).offset(skip).limit(limit))
    donations = result.scalars().all()
    return [Donation.from_orm(donation) for donation in donations]

@router.get("/donations/{donation_id}", response_model=Donation)
async def read_donation(donation_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(DonationModel).filter(DonationModel.id == donation_id))
    donation = result.scalar_one_or_none()
    if donation is None:
        raise HTTPException(status_code=404, detail="Donation not found")
    return Donation.from_orm(donation)

@router.put("/donations/{donation_id}", response_model=Donation)
async def update_donation(donation_id: str, donation: Donation, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(DonationModel).filter(DonationModel.id == donation_id))
    db_donation = result.scalar_one_or_none()
    if db_donation is None:
        raise HTTPException(status_code=404, detail="Donation not found")
    
    for key, value in donation.dict(exclude_unset=True).items():
        setattr(db_donation, key, value)
    
    await db.commit()
    await db.refresh(db_donation)
    return Donation.from_orm(db_donation)

@router.delete("/donations/{donation_id}", response_model=Donation)
async def delete_donation(donation_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(DonationModel).filter(DonationModel.id == donation_id))
    donation = result.scalar_one_or_none()
    if donation is None:
        raise HTTPException(status_code=404, detail="Donation not found")
    await db.delete(donation)
    await db.commit()
    return Donation.from_orm(donation)

@router.patch("/donations/{donation_id}/status", response_model=Donation)
async def update_donation_status(donation_id: str, status: DonationStatus, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(DonationModel).filter(DonationModel.id == donation_id))
    donation = result.scalar_one_or_none()
    if donation is None:
        raise HTTPException(status_code=404, detail="Donation not found")
    donation.status = status
    await db.commit()
    await db.refresh(donation)
    return Donation.from_orm(donation)

@router.patch("/donations/{donation_id}/agency", response_model=Donation)
async def update_donation_agency(donation_id: str, agency_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(DonationModel).filter(DonationModel.id == donation_id))
    donation = result.scalar_one_or_none()
    if donation is None:
        raise HTTPException(status_code=404, detail="Donation not found")
    donation.agency_id = agency_id
    await db.commit()
    await db.refresh(donation)
    return Donation.from_orm(donation)

@router.patch("/donations/{donation_id}/location", response_model=Donation)
async def update_donation_location(donation_id: str, location: Tuple[float, float], db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(DonationModel).filter(DonationModel.id == donation_id))
    donation = result.scalar_one_or_none()
    if donation is None:
        raise HTTPException(status_code=404, detail="Donation not found")
    donation.location = location
    await db.commit()
    await db.refresh(donation)
    return Donation.from_orm(donation)