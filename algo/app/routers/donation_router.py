from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from db.database import get_db
from db.models import DonationModel, AgencyModel, RequirementModel, DonorModel
from schemas.Donation import Donation, DonationCreated
from schemas.Agency import Agency
from schemas.Requirement import Requirement
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


class DonationLocationUpdate(BaseModel):
    location: Tuple[float, float]


class DonationResponse(BaseModel):
    donation_id: UUID
    agency_id: UUID
    action: str
    success: bool


@router.post("/donations/{donation_id}/{action}", response_model=DonationResponse)
async def handle_donation_response(
    donation_id: UUID,
    action: str,
    db: AsyncSession = Depends(get_db),
    allocation_system: AsyncSession = Depends(get_allocation_system),
    current_user=Depends(get_current_user)
):
    try:
        if action not in ['accept', 'reject']:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid action. Must be 'accept' or 'reject'."
            )

        if current_user["role"] != "Beneficiary":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Unauthorized user. Agency role required."
            )

        # check if the agency exists
        result = await db.execute(
            select(AgencyModel).filter(
                AgencyModel.name == current_user["company_name"]
            )
        )
        agency: AgencyModel = result.scalars().first()

        if agency is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Agency not found"
            )

        # Process the action
        if action == 'accept':
            success = await allocation_system.accept_donation(donation_id, agency.id)
        else:  # action == 'reject'
            success = await allocation_system.reject_donation(donation_id, agency.id)

        message = (
            f"""Failed to {action} the donation (ID: {donation_id}) for agency (ID: {agency.id}).
            This could be because the donation has already been processed, the agency is not first in the allocation queue,
            or there was an unexpected issue. Please check the current status of the donation and try again if necessary."""
        )

        if not success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=message
            )

        return DonationResponse(
            donation_id=donation_id,
            agency_id=agency.id,
            action=action,
            success=success
        )

    except HTTPException as http_err:
        print(f"HTTP error during donation {action}: {str(http_err)}")
        raise http_err

    except Exception as e:
        print(f"Unexpected error during donation {action}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while processing the donation."
        )


async def get_allocation_system(request):
    return request.app.state.allocation_system

# Temporary function for non-routed reads


async def fetch_agencies(db: AsyncSession, skip: int = 0, limit: int = 100):
    result = await db.execute(select(AgencyModel).offset(skip).limit(limit))
    agencies = result.scalars().all()
    return [Agency.model_validate(agency) for agency in agencies]

# Temporary function for non-routed reads


async def fetch_requirements(db: AsyncSession, skip: int = 0, limit: int = 100):
    result = await db.execute(select(RequirementModel).offset(skip).limit(limit))
    requirements = result.scalars().all()
    return [Requirement.model_validate(agency) for agency in requirements]


@router.post("/donations/me", response_model=Donation)
async def create_donation_as_me(
    donation_created: DonationCreated,
    db: AsyncSession = Depends(get_db),
    allocation_system: AsyncSession = Depends(get_allocation_system),
    current_user=Depends(get_current_user)
):
    result = await db.execute(
        select(DonorModel).filter(
            DonorModel.name == current_user["company_name"]
        )
    )
    donors = result.scalars().all()

    if not donors:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Donor not found"
        )

    donor = donors[0]

    donation = Donation(
        donor_id=donor.id,
        food_type=donation_created.food_type,
        quantity=donation_created.quantity,
        location=donation_created.location,
        status=donation_created.status,
        expiry_time=donation_created.expiry_time
    )

    # db_donation = DonationModel(**donation.model_dump())
    db.add(donation)
    await db.commit()
    await db.refresh(donation)

    agencies = await fetch_agencies(db)
    await allocation_system.allocate_donation(donation, agencies)

    return Donation.model_validate(donation)


@ router.post("/donations", response_model=Donation)
async def create_donation(donation: Donation, request: Request, db: AsyncSession = Depends(get_db)
                          ):
    allocation_system = await get_allocation_system(request)
    # db_donation = DonationModel(**donation.model_dump())
    db.add(donation)
    await db.commit()
    await db.refresh(donation)

    agencies = await fetch_agencies(db)
    # requirements = await fetch_requirements(db)
    await allocation_system.allocate_donation(donation, agencies)

    return Donation.model_validate(donation)


@ router.get("/donations", response_model=List[Donation])
async def read_donations(skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(DonationModel).offset(skip).limit(limit))
    donations = result.scalars().all()
    return [Donation.model_validate(donation) for donation in donations]


@ router.get("/donations/me", response_model=List[Donation])
async def read_donations_as_me(
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user)
):
    try:
        if current_user["role"] == "Beneficiary":

            # check if the agency exists
            result = await db.execute(
                select(AgencyModel).filter(
                    AgencyModel.name == current_user["company_name"]
                )
            )
            agencies: List[AgencyModel] = result.scalars().all()

            if not agencies:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Agency not found"
                )

            agency = agencies[0]

            # retrieve all donations for the agency
            result = await db.execute(
                select(DonationModel).filter(
                    DonationModel.agency_id == agency.id)
            )
            donations = result.scalars().all()

            return [Donation.model_validate(donation) for donation in donations]

        elif current_user["role"] == "Donor":

            # check if the donor exists
            result = await db.execute(
                select(DonorModel).filter(
                    DonorModel.name == current_user["company_name"]
                )
            )
            donors: List[DonorModel] = result.scalars().all()

            if not donors:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Donor not found"
                )

            donor = donors[0]

            # retrieve all donations for the donor
            result = await db.execute(
                select(DonationModel).filter(
                    DonationModel.donor_id == donor.id)
            )
            donations = result.scalars().all()

            return [Donation.model_validate(donation) for donation in donations]
        elif current_user["role"] == "Volunteer":
            pass
        else:
            raise HTTPException(
                status_code=400,
                detail="Role not found"
            )

    except HTTPException as e:
        raise e

    except Exception as e:
        print(f"Unexpected error in read_donation_as_me: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while retrieving the donation"
        )


@ router.get("/donations/{donation_id}", response_model=Donation)
async def read_donation(donation_id: UUID, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(DonationModel).filter(DonationModel.id == donation_id))
    donation = result.scalar_one_or_none()
    if donation is None:
        raise HTTPException(status_code=404, detail="Donation not found")
    return Donation.model_validate(donation)


@ router.put("/donations/{donation_id}", response_model=Donation)
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


@ router.delete("/donations/{donation_id}", response_model=Donation)
async def delete_donation(donation_id: UUID, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(DonationModel).filter(DonationModel.id == donation_id))
    donation = result.scalar_one_or_none()
    if donation is None:
        raise HTTPException(status_code=404, detail="Donation not found")
    await db.delete(donation)
    await db.commit()
    return Donation.model_validate(donation)


@ router.patch("/donations/{donation_id}/status", response_model=Donation)
async def update_donation_status(donation_id: UUID, update_data: DonationStatusUpdate, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(DonationModel).filter(DonationModel.id == donation_id))
    donation = result.scalar_one_or_none()
    if donation is None:
        raise HTTPException(status_code=404, detail="Donation not found")
    donation.status = update_data.status
    await db.commit()
    await db.refresh(donation)
    return Donation.model_validate(donation)


@ router.patch("/donations/{donation_id}/agency", response_model=Donation)
async def update_donation_agency(donation_id: UUID, update_data: AgencyUpdate, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(DonationModel).filter(DonationModel.id == donation_id))
    donation = result.scalar_one_or_none()
    if donation is None:
        raise HTTPException(status_code=404, detail="Donation not found")
    donation.agency_id = update_data.agency_id
    await db.commit()
    await db.refresh(donation)
    return Donation.model_validate(donation)


@ router.patch("/donations/{donation_id}/location", response_model=Donation)
async def update_donation_location(donation_id: UUID, update_data: DonationLocationUpdate, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(DonationModel).filter(DonationModel.id == donation_id))
    donation = result.scalar_one_or_none()
    if donation is None:
        raise HTTPException(status_code=404, detail="Donation not found")
    donation.location = update_data.location
    await db.commit()
    await db.refresh(donation)

    return Donation.model_validate(donation)
