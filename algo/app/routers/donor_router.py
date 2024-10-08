from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from db.database import get_db
from db.models import DonorModel
from schemas.Donor import Donor, DonorLocationUpdate, DonorDonationsUpdate
from typing import List, Tuple
from uuid import UUID
from pydantic import BaseModel
from utils.jwt_auth import get_current_user

router = APIRouter()


class DonorLocationUpdate(BaseModel):
    location: Tuple[float, float]


class DonorDonationsUpdate(BaseModel):
    donations: float


@router.post("/donors", response_model=Donor)
async def create_donor(
        db: AsyncSession = Depends(get_db),
        current_user=Depends(get_current_user)):

    if current_user["role"] != "Donor":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authorized to create a donor."
        )

    # check if a company_name matches name
    result = await db.execute(select(DonorModel).filter_by(name=current_user["company_name"]))
    donors = result.scalars().all()

    if not donors:
        # if dont match, create the company
        donor = Donor(
            name=current_user["company_name"]
        )
    else:
        donor = donors[0]

    # db_donor = DonorModel(**donor.model_dump())
    db.add(donor)
    await db.commit()
    await db.refresh(donor)
    return Donor.model_validate(donor)


@router.get("/donors", response_model=List[Donor])
async def read_donors(skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(DonorModel).offset(skip).limit(limit))
    donors = result.scalars().all()
    return [Donor.model_validate(donor) for donor in donors]


@router.get("/donors/me", response_model=Donor)
async def read_donor_as_me(
        db: AsyncSession = Depends(get_db),
        current_user=Depends(get_current_user)):

    if current_user["role"] != "Donor":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authorized to read a donor."
        )

    result = await db.execute(select(DonorModel).filter(DonorModel.name == current_user["company_name"]))
    donors = result.scalars().all()

    if not donors:
        raise HTTPException(status_code=404, detail="Donor not found")

    donor = donors[0]

    return Donor.from_orm(donor)


@router.get("/donors/{donor_id}", response_model=Donor)
async def read_donor(donor_id: UUID, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(DonorModel).filter(DonorModel.id == donor_id))
    donor = result.scalar_one_or_none()
    if donor is None:
        raise HTTPException(status_code=404, detail="Donor not found")
    return Donor.model_validate(donor)

# @router.put("/donors/{donor_id}", response_model=Donor)
# async def update_donor(donor_id: str, donor: Donor, db: AsyncSession = Depends(get_db)):
#     result = await db.execute(select(DonorModel).filter(DonorModel.id == donor_id))
#     db_donor = result.scalar_one_or_none()
#     if db_donor is None:
#         raise HTTPException(status_code=404, detail="Donor not found")

#     for key, value in donor.dict(exclude_unset=True).items():
#         setattr(db_donor, key, value)

#     await db.commit()
#     await db.refresh(db_donor)
#     return Donor.from_orm(db_donor)


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


@router.patch("/donors/me/location", response_model=Donor)
async def update_donor_location_me(
        req: DonorLocationUpdate,
        db: AsyncSession = Depends(get_db),
        current_user=Depends(get_current_user)):

    if current_user["role"] != "Donor":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authorized to update a donor location."
        )

    location: Tuple[float, float] = tuple(req.location)

    result = await db.execute(select(DonorModel).filter(DonorModel.name == current_user["company_name"]))
    donor = result.scalar_one_or_none()
    if donor is None:
        raise HTTPException(status_code=404, detail="Donor not found")
    donor.location = location

    await db.commit()
    await db.refresh(donor)
    return Donor.from_orm(donor)


@router.patch("/donors/{donor_id}/location", response_model=Donor)
async def update_donor_location(donor_id: str, location_update: DonorLocationUpdate, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(DonorModel).filter(DonorModel.id == donor_id))
    donor = result.scalar_one_or_none()
    if donor is None:
        raise HTTPException(status_code=404, detail="Donor not found")
    donor.location = location_update.location
    await db.commit()
    await db.refresh(donor)
    return Donor.model_validate(donor)


@router.patch("/donors/{donor_id}/donations", response_model=Donor)
async def update_donor_donations(donor_id: str, donations_update: DonorDonationsUpdate, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(DonorModel).filter(DonorModel.id == donor_id))
    donor = result.scalar_one_or_none()
    if donor is None:
        raise HTTPException(status_code=404, detail="Donor not found")
    donor.donations = donations_update.donations
    await db.commit()
    await db.refresh(donor)

    return Donor.model_validate(donor)
