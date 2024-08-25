from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from db.database import get_db
from db.models import DonorModel
from schemas.Donor import Donor
from typing import List, Tuple
from uuid import UUID

router = APIRouter()

@router.post("/donors", response_model=Donor)
async def create_donor(donor: Donor, db: AsyncSession = Depends(get_db)):
    db_donor = DonorModel(**donor.model_dump())
    db.add(db_donor)
    await db.commit()
    await db.refresh(db_donor)
    return Donor.model_validate(db_donor)

@router.get("/donors", response_model=List[Donor])
async def read_donors(skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(DonorModel).offset(skip).limit(limit))
    donors = result.scalars().all()
    return [Donor.model_validate(donor) for donor in donors]

@router.get("/donors/{donor_id}", response_model=Donor)
async def read_donor(donor_id: UUID, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(DonorModel).filter(DonorModel.id == donor_id))
    donor = result.scalar_one_or_none()
    if donor is None:
        raise HTTPException(status_code=404, detail="Donor not found")
    return Donor.model_validate(donor)

@router.put("/donors/{donor_id}", response_model=Donor)
async def update_donor(donor_id: UUID, donor: Donor, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(DonorModel).filter(DonorModel.id == donor_id))
    db_donor = result.scalar_one_or_none()
    if db_donor is None:
        raise HTTPException(status_code=404, detail="Donor not found")
    
    for key, value in donor.dict(exclude_unset=True).items():
        setattr(db_donor, key, value)
    
    await db.commit()
    await db.refresh(db_donor)
    return Donor.model_validate(db_donor)

@router.delete("/donors/{donor_id}", response_model=Donor)
async def delete_donor(donor_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(DonorModel).filter(DonorModel.id == donor_id))
    donor = result.scalar_one_or_none()
    if donor is None:
        raise HTTPException(status_code=404, detail="Donor not found")
    await db.delete(donor)
    await db.commit()
    return Donor.model_validate(donor)

@router.patch("/donors/{donor_id}/location", response_model=Donor)
async def update_donor_location(donor_id: str, location: Tuple[float, float], db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(DonorModel).filter(DonorModel.id == donor_id))
    donor = result.scalar_one_or_none()
    if donor is None:
        raise HTTPException(status_code=404, detail="Donor not found")
    donor.location = location
    await db.commit()
    await db.refresh(donor)
    return Donor.model_validate(donor)

@router.patch("/donors/{donor_id}/donations", response_model=Donor)
async def update_donor_donations(donor_id: str, donations: float, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(DonorModel).filter(DonorModel.id == donor_id))
    donor = result.scalar_one_or_none()
    if donor is None:
        raise HTTPException(status_code=404, detail="Donor not found")
    donor.donations = donations
    await db.commit()
    await db.refresh(donor)
    return Donor.model_validate(donor)