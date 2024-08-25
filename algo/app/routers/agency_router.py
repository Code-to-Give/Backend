from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from db.database import get_db
from db.models import AgencyModel
from schemas.Agency import Agency, AgencyRequirementsUpdate, AgencyPriorityFlagUpdate, AgencyLocationUpdate
from typing import List, Dict, Tuple
from uuid import UUID
from utils.jwt_auth import get_current_user
from pydantic import BaseModel

router = APIRouter()


class AgencyUpdate(BaseModel):
    agency_id: UUID


class AgencyRequirementsUpdate(BaseModel):
    requirements: Dict[str, int]


class AgencyPriorityFlagUpdate(BaseModel):
    priority_flag: bool


class AgencyLocationUpdate(BaseModel):
    location: Tuple[float, float]


@router.post("/agencies", response_model=Agency)
async def create_agency(
        db: AsyncSession = Depends(get_db),
        current_user=Depends(get_current_user)):

    if current_user["role"] != "Beneficiary":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authorized to create an agency."
        )

    # check if a company_name matches name
    result = await db.execute(select(AgencyModel).filter_by(name=current_user["company_name"]))
    existing_agency = result.scalars().first()

    # if matches then dont create
    if existing_agency:
        return existing_agency

    agency = AgencyModel(
        name=current_user["company_name"]
    )

    db_agency = AgencyModel(**agency.model_dump())
    db.add(db_agency)
    await db.commit()
    await db.refresh(db_agency)
    return Agency.model_validate(db_agency)


@router.get("/agencies", response_model=List[Agency])
async def read_agencies(skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(AgencyModel).offset(skip).limit(limit))
    agencies = result.scalars().all()
    return [Agency.model_validate(agency) for agency in agencies]


@router.get("/agencies/me", response_model=Agency)
async def read_agency_as_me(
        db: AsyncSession = Depends(get_db),
        current_user=Depends(get_current_user)):

    if current_user["role"] != "Beneficiary":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authorized to read an agency."
        )

    result = await db.execute(select(AgencyModel).filter(AgencyModel.name == current_user["company_name"]))
    agency = result.scalar_one_or_none()
    if agency is None:
        raise HTTPException(status_code=404, detail="Agency not found")
    return Agency.model_validate(agency)


@router.get("/agencies/{agency_id}", response_model=Agency)
async def read_agency(agency_id: UUID, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(AgencyModel).filter(AgencyModel.id == agency_id))
    agency = result.scalar_one_or_none()
    if agency is None:
        raise HTTPException(status_code=404, detail="Agency not found")
    return Agency.model_validate(agency)


@router.put("/agencies/{agency_id}", response_model=Agency)
async def update_agency(agency_id: UUID, agency: Agency, db: AsyncSession = Depends(get_db)):

    result = await db.execute(select(AgencyModel).filter(AgencyModel.id == agency_id))
    agency = result.scalar_one_or_none()
    if agency is None:
        raise HTTPException(status_code=404, detail="Agency not found")
    return Agency.model_validate(agency)


@router.delete("/agencies/{agency_id}", response_model=Agency)
async def delete_agency(agency_id: UUID, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(AgencyModel).filter(AgencyModel.id == agency_id))
    agency = result.scalar_one_or_none()
    if agency is None:
        raise HTTPException(status_code=404, detail="Agency not found")
    await db.delete(agency)
    await db.commit()
    return Agency.model_validate(agency)


@router.patch("/agencies/{agency_id}/requirements", response_model=Agency)
async def update_agency_requirements(agency_id: UUID, requirements_update: AgencyRequirementsUpdate, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(AgencyModel).filter(AgencyModel.id == agency_id))
    agency = result.scalar_one_or_none()
    if agency is None:
        raise HTTPException(status_code=404, detail="Agency not found")
    agency.requirements = requirements_update.requirements
    await db.commit()
    await db.refresh(agency)
    return Agency.model_validate(agency)


@router.patch("/agencies/{agency_id}/priority-flag", response_model=Agency)
async def set_agency_priority_flag(agency_id: UUID, priority_update: AgencyPriorityFlagUpdate, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(AgencyModel).filter(AgencyModel.id == agency_id))
    agency = result.scalar_one_or_none()
    if agency is None:
        raise HTTPException(status_code=404, detail="Agency not found")
    agency.priority_flag = priority_update.priority_flag
    await db.commit()
    await db.refresh(agency)
    return Agency.model_validate(agency)


@router.patch("/agencies/{agency_id}/location", response_model=Agency)
async def update_agency_location(agency_id: UUID, location_update: AgencyLocationUpdate, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(AgencyModel).filter(AgencyModel.id == agency_id))
    agency = result.scalar_one_or_none()
    if agency is None:
        raise HTTPException(status_code=404, detail="Agency not found")
    agency.location = location_update.location
    await db.commit()
    await db.refresh(agency)

    return Agency.model_validate(agency)
