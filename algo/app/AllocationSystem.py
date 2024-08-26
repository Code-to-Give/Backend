from pydantic import BaseModel, ConfigDict
from typing import List, Dict, Optional
from uuid import UUID, uuid4
import asyncio
from datetime import datetime, timedelta
from geopy.distance import geodesic
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import update
from db.database import get_db
from db.models import AgencyModel, DonationModel, RequirementModel
from schemas.Agency import Agency
from schemas.FoodType import FoodType
from schemas.Requirement import Requirement
from schemas.Donation import Donation
from schemas.DonationStatus import DonationStatus
from fastapi import Depends


class AllocationSystem():

    def __init__(self, db):
        self.db = db
        self.queue_move_interval = int = 600
        self.allocation_queues = {}
        self.allocation_timers = {}
        self.agency_requirements = {}

    _instance = None

    @classmethod
    async def get_instance(cls, db: AsyncSession = None):
        if cls._instance is None:
            if db is None:
                raise ValueError(
                    "Database session is required for initialization")
            cls._instance = cls(db=db)
            await cls._instance.initialize()
        return cls._instance

    async def initialize(self):
        await self.load_requirements()
        await self.recover_pending_donations()

    async def load_requirements(self):
        """Load all existing requirements from the database."""
        requirements = await self.get_all_requirements_from_db()
        for req in requirements:
            self.update_agency_requirement(req)

    async def recover_pending_donations(self):
        """Recover and reinitialize allocation for pending donations."""
        pending_donations = await self.get_pending_donations_from_db()
        agencies = await self.get_all_agencies_from_db()

        for donation in pending_donations:
            print(f"Recovering allocation for Donation {donation.id}")
            await self.allocate_donation(donation, agencies)

    def update_agency_requirement(self, requirement: Requirement):
        """Update a single requirement for an agency."""
        if requirement.agency_id not in self.agency_requirements:
            self.agency_requirements[requirement.agency_id] = {}
        self.agency_requirements[requirement.agency_id][requirement.food_type] = requirement.quantity

    async def allocate_donation(self, donation: Donation, agencies: List[Agency]) -> None:
        """Allocate a donation to the most suitable agencies."""
        sorted_agencies = sorted(
            agencies,
            key=lambda agency: (
                -agency.priority_flag,
                self.compute_distance(agency.location, donation.location),
                -self.compute_needs_score(self.agency_requirements.get(
                    agency.id, {}), donation.food_type, donation.quantity)
            )
        )

        self.allocation_queues[donation.id] = [
            agency.id for agency in sorted_agencies]
        self.allocation_timers[donation.id] = datetime.now(
        ) + timedelta(seconds=self.queue_move_interval)
        donation.status = DonationStatus.ALLOCATED

        # changes here
        if self.allocation_queues[donation.id]:
            donation.agency_id = self.allocation_queues[donation.id][0]

        await self.update_donation_in_db(donation)

        # Start the allocation management task for this donation
        asyncio.create_task(self.manage_allocation(donation))

    async def manage_allocation(self, donation: Donation):
        while donation.id in self.allocation_queues and self.allocation_queues[donation.id]:
            now = datetime.now()
            if now >= self.allocation_timers[donation.id]:
                # Move to the next agency in the queue
                self.allocation_queues[donation.id].pop(0)
                if self.allocation_queues[donation.id]:
                    donation.agency_id = self.allocation_queues[donation.id][0]
                    await self.update_donation_in_db(donation)
                    self.allocation_timers[donation.id] = now + \
                        timedelta(seconds=self.queue_move_interval)
                    print(
                        f"Moved Donation {donation.id} to next agency {self.allocation_queues[donation.id][0]}")
                else:
                    print(
                        f"No more agencies available for Donation {donation.id}")
                    donation.status = DonationStatus.READY
                    await self.update_donation_in_db(donation)
                    del self.allocation_queues[donation.id]
                    del self.allocation_timers[donation.id]
            await asyncio.sleep(10)  # Check every 10 seconds

    def compute_distance(self, agency_location: List[float], donation_location: List[float]) -> float:
        """Compute distance in km between 2 points of lat/long."""
        return geodesic(tuple(agency_location), tuple(donation_location)).km

    def compute_needs_score(self, agency_requirements: Dict[FoodType, int], donation_food_type: FoodType, donation_quantity: int) -> int:
        """Compute a score based on how well the donation meets the agency's requirements."""
        if donation_food_type in agency_requirements:
            return min(agency_requirements[donation_food_type], donation_quantity)
        return 0

    async def accept_donation(self, donation_id: UUID, agency_id: UUID):
        if donation_id in self.allocation_queues and self.allocation_queues[donation_id][0] == agency_id:
            donation = await self.get_donation_from_db(donation_id)
            donation.status = DonationStatus.ACCEPTED
            donation.agency_id = agency_id
            await self.update_donation_in_db(donation)
            del self.allocation_queues[donation_id]
            del self.allocation_timers[donation_id]
            print(f"Donation {donation_id} accepted by Agency {agency_id}")
            return True
        return False

    async def reject_donation(self, donation_id: UUID, agency_id: UUID):
        if donation_id in self.allocation_queues and self.allocation_queues[donation_id][0] == agency_id:
            self.allocation_queues[donation_id].pop(0)
            if self.allocation_queues[donation_id]:
                self.allocation_timers[donation_id] = datetime.now(
                ) + timedelta(seconds=self.queue_move_interval)
                print(
                    f"Donation {donation_id} rejected by Agency {agency_id}. Moved to next agency.")
            else:
                donation = await self.get_donation_from_db(donation_id)
                donation.status = DonationStatus.READY
                await self.update_donation_in_db(donation)
                del self.allocation_queues[donation_id]
                del self.allocation_timers[donation_id]
                print(
                    f"Donation {donation_id} rejected by last agency. Marked as READY.")
            return True
        return False

    async def get_all_requirements_from_db(self) -> List[Requirement]:
        result = await self.db.execute(select(RequirementModel))
        requirements = result.scalars().all()
        return [Requirement.model_validate(req) for req in requirements]

    async def get_pending_donations_from_db(self) -> List[Donation]:
        result = await self.db.execute(
            select(DonationModel).filter(
                DonationModel.status.in_(
                    [DonationStatus.READY, DonationStatus.ALLOCATED])
            )
        )
        donations = result.scalars().all()
        return [Donation.model_validate(donation) for donation in donations]

    async def get_all_agencies_from_db(self) -> List[Agency]:
        result = await self.db.execute(select(AgencyModel))
        agencies = result.scalars().all()
        return [Agency.model_validate(agency) for agency in agencies]

    async def get_donation_from_db(self, donation_id: UUID) -> Donation:
        result = await self.db.execute(
            select(DonationModel).filter(DonationModel.id == donation_id)
        )
        donation = result.scalar_one_or_none()
        if donation is None:
            raise ValueError(f"Donation with id {donation_id} not found")
        return Donation.model_validate(donation)

    async def update_donation_in_db(self, donation: Donation):
        stmt = (
            update(DonationModel)
            .where(DonationModel.id == donation.id)
            .values(**donation.model_dump(exclude={"id"}))
        )
        await self.db.execute(stmt)
        await self.db.commit()


async def get_allocation_system(db: AsyncSession = Depends(get_db)) -> AllocationSystem:
    return await AllocationSystem.get_instance(db)


# This function should be called when a new requirement is added or updated
def update_requirement(requirement: Requirement):
    allocation_system = get_allocation_system()
    allocation_system.update_agency_requirement(requirement)
