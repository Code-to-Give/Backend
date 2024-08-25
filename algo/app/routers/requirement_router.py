from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.dialects.postgresql import insert
from db.database import get_db
from db.models import RequirementModel
from schemas.Requirement import Requirement
from typing import List
from uuid import UUID
from pydantic import BaseModel

router = APIRouter()

class RequirementUpdate(BaseModel):
    quantity: int

@router.post("/requirements", response_model=Requirement)
async def create_requirement(requirement: Requirement, db: AsyncSession = Depends(get_db)):
    stmt = insert(RequirementModel).values(
        id=requirement.id,
        agency_id=requirement.agency_id,
        food_type=requirement.food_type,
        quantity=requirement.quantity
    )
    stmt = stmt.on_conflict_do_update(
        constraint='uq_agency_food_type',
        set_=dict(quantity=stmt.excluded.quantity)
    )
    await db.execute(stmt)
    await db.commit()
    
    # Fetch the upserted requirement
    result = await db.execute(
        select(RequirementModel)
        .filter(RequirementModel.agency_id == requirement.agency_id, RequirementModel.food_type == requirement.food_type)
    )
    db_requirement = result.scalar_one_or_none()
    if db_requirement is None:
        raise HTTPException(status_code=404, detail="Requirement not found after upsert")
    return Requirement.model_validate(db_requirement)

@router.get("/requirements", response_model=List[Requirement])
async def read_requirements(skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(RequirementModel).offset(skip).limit(limit))
    requirements = result.scalars().all()
    return [Requirement.model_validate(requirement) for requirement in requirements]

@router.get("/requirements/{requirement_id}", response_model=Requirement)
async def read_requirement(requirement_id: UUID, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(RequirementModel).filter(RequirementModel.id == requirement_id))
    requirement = result.scalar_one_or_none()
    if requirement is None:
        raise HTTPException(status_code=404, detail="Requirement not found")
    return Requirement.model_validate(requirement)

@router.put("/requirements/{requirement_id}", response_model=Requirement)
async def update_requirement(requirement_id: UUID, requirement: RequirementUpdate, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(RequirementModel).filter(RequirementModel.id == requirement_id))
    db_requirement = result.scalar_one_or_none()
    if db_requirement is None:
        raise HTTPException(status_code=404, detail="Requirement not found")
    
    db_requirement.quantity = requirement.quantity
    
    await db.commit()
    await db.refresh(db_requirement)
    return Requirement.model_validate(db_requirement)

@router.delete("/requirements/{requirement_id}", response_model=Requirement)
async def delete_requirement(requirement_id: UUID, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(RequirementModel).filter(RequirementModel.id == requirement_id))
    requirement = result.scalar_one_or_none()
    if requirement is None:
        raise HTTPException(status_code=404, detail="Requirement not found")
    await db.delete(requirement)
    await db.commit()
    return Requirement.model_validate(requirement)

@router.get("/agencies/{agency_id}/requirements", response_model=List[Requirement])
async def read_agency_requirements(agency_id: UUID, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(RequirementModel).filter(RequirementModel.agency_id == agency_id))
    requirements = result.scalars().all()
    return [Requirement.model_validate(requirement) for requirement in requirements]