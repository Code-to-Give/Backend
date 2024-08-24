from pydantic import BaseModel
from typing import List, Dict, Optional
from schemas.FoodType import FoodType
from schemas.Agency import Agency
from schemas.Donation import Donation
from schemas.Donor import Donor
from schemas.DonationStatus import DonationStatus
from uuid import UUID, uuid4
import asyncio
import random
from geopy.distance import geodesic

class AllocationSystem(BaseModel):
    request_timeout: float = 300.0 # 5 minute timeout
    
    async def allocate_donation(self, donation, agencies: List) -> Optional[UUID]:
        """Allocate a donation to the most suitable agency."""
        
        # Step 1: Sort agencies based on priority, distance, and needs
        sorted_agencies = sorted(
            agencies,
            key=lambda agency: (
                -agency.priority_flag,  # Sort priority agencies first (True > False)
                self.compute_distance(agency.location, donation.location),  # Then sort by distance (closest first)
                self.compute_needs_score(agency.requirements, donation.items)  # Then by needs (most overlap first)
            )
        )
        
        # Step 2: Attempt allocation with timeout. First in queue is sent push notification (to be implemented). Moves on to next after timeout.
        for agency in sorted_agencies:
            try:
                donation.status = DonationStatus.ALLOCATED
                accepted = await asyncio.wait_for(self.send_allocation_request(agency, donation), timeout=self.request_timeout)
                if accepted:
                    print(f"Donation {donation.id} accepted by Agency {agency.id}")
                    return agency.id
                else:
                    print(f"Donation {donation.id} rejected by Agency {agency.id}. Moving to next agency.")
            except asyncio.TimeoutError:
                print(f"Allocation request to Agency {agency.id} timed out. Moving to next agency.")
        
        print("No response.")
        return None
    
    def compute_distance(self, agency_location:tuple[float, float], donation_location: tuple[float, float]) -> float:
        """Compute distance in km between 2 points of lat/long."""
        return geodesic(agency_location, donation_location).km
    
    def compute_needs_score(self, agency_requirements: Dict[FoodType, int], donation_items: Dict[FoodType, int]) -> int:
        """Compute a score based on how well the donation meets the agency's requirements."""
        score = 0
        for food_type, quantity in agency_requirements.items():
            if food_type in donation_items:
                # Increment score by the minimum of required vs donated
                score += min(quantity, donation_items[food_type])
        return score
    
    # NOT IMPLEMENTED YET, we test with some sleep, random accept
    async def send_allocation_request(self, agency, donation):
        await asyncio.sleep(5)
        
        return random.choice([True, False])

async def test():
    # sample donation
    sample_donation = Donation(
    donor_id="donor123",
    items={
        FoodType.HALAL: 5,
        FoodType.VEGAN: 3
    },
    location=(1.3, 104),
    status=DonationStatus.READY,
    agency_id=None, # No agency assigned yet
    )
    
    # sample agencies
    agencies = [
        Agency(
            id = "1",
            priority_flag=False,
            location=(1.3, 103.8), 
            requirements={FoodType.VEGAN: 2, FoodType.HALAL: 5},
            name="agency1"
        ),
        Agency(
            id = "2",
            name="agency2",
            priority_flag=True,
            location=(1.45, 103.8), 
            requirements={FoodType.HALAL: 2}
        ),
        Agency(
            id = "3",
            name="agency3",
            priority_flag=True,
            location=(1.5000, 104),
            requirements={FoodType.HALAL: 4, FoodType.VEGAN: 2}
        )
    ]
    
    allocation_system = AllocationSystem()

    result = await allocation_system.allocate_donation(sample_donation, agencies)

    print(f"Allocation result: {result}")

if __name__ == '__main__':
    asyncio.run(test())
    
