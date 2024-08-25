from pydantic import BaseModel, ConfigDict
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
from fastapi import WebSocket

class AllocationSystem(BaseModel):
    request_timeout: float = 300.0 # 5 minute timeout
    connections: Dict[str, WebSocket] = {} # hashmap of agency to websockets
    
    model_config = ConfigDict(arbitrary_types_allowed=True)
    async def allocate_donation(self, donation, agencies: List) -> Optional[UUID]:
        """Allocate a donation to the most suitable agency."""
        
        # Step 1: Sort agencies based on priority, distance, and needs
        sorted_agencies = sorted(
            agencies,
            key=lambda agency: (
                -agency.priority_flag,  # Sort priority agencies first (True > False)
                self.compute_distance(agency.location, donation.location),  # Then sort by distance (closest first)
                self.compute_needs_score(agency.requirements, donation.food_type, donation.quantity)  # Then by needs (most overlap first)
            )
        )
        
        # Step 2: Attempt allocation with timeout. First in queue is sent push notification (to be implemented). Moves on to next after timeout.
        for agency in sorted_agencies:
            try:
                donation.status = DonationStatus.ALLOCATED
                accepted = await asyncio.wait_for(self.send_allocation_request(agency, donation), timeout=self.request_timeout)
                if accepted:
                    print(f"Donation {donation.id} accepted by Agency {agency.id}")
                    donation.status = DonationStatus.ACCEPTED
                    return agency.id
                else:
                    print(f"Donation {donation.id} rejected by Agency {agency.id}. Moving to next agency.")
            except asyncio.TimeoutError:
                print(f"Allocation request to Agency {agency.id} timed out. Moving to next agency.")
        donation.status = DonationStatus.READY
        print("No response.")
        return None
    
    def compute_distance(self, agency_location:tuple[float, float], donation_location: tuple[float, float]) -> float:
        """Compute distance in km between 2 points of lat/long."""
        return geodesic(agency_location, donation_location).km
    
    def compute_needs_score(self, agency_requirements: Dict[FoodType, int], donation_food_type: FoodType, donation_quantity: int) -> int:
        """Compute a score based on how well the donation meets the agency's requirements."""
        score = 0
        
        # Check if the donation's food type is in the agency's requirements
        if donation_food_type in agency_requirements:
            # Compute score as the minimum of the required quantity and donated quantity
            score = min(agency_requirements[donation_food_type], donation_quantity)
        
        return score
    
    # NOT IMPLEMENTED YET, we test with some sleep, random accept
    async def send_allocation_request_test(self, agency, donation):
        await asyncio.sleep(5)
        
        return random.choice([True, False])
    
    async def send_allocation_request(self, agency, donation):
        if agency.id in self.connections:
            ws = self.connections[agency.id]
            await ws.send_json({"type": "allocation_request", "donation": donation.dict()})
            response = await ws.receive_json()
            return response.get("accepted", False)
        else:
            print(f"No WebSocket connection for Agency {agency.id}")
            return False

    async def connect(self, websocket: WebSocket, agency_id: str):
        await websocket.accept()
        self.connections[agency_id] = websocket

    async def disconnect(self, agency_id: str):
        if agency_id in self.connections:
            del self.connections[agency_id]

async def test():
    # sample donation
    sample_donation = Donation(
    donor_id="donor123",
    food_type=FoodType.HALAL,
    quantity=100,
    location=(1.3, 104),
    status=DonationStatus.READY,
    agency_id="None", # No agency assigned yet
    )
    
    # sample agencies
    agencies = [
        Agency(
            id = "1",
            priority_flag=False,
            location=(1.3, 103.8), 
            requirements={FoodType.VEGETARIAN: 2, FoodType.HALAL: 5},
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
            requirements={FoodType.HALAL: 4, FoodType.VEGETARIAN: 2}
        )
    ]
    
    allocation_system = AllocationSystem()

    result = await allocation_system.allocate_donation_test(sample_donation, agencies)

    print(f"Allocation result: {result}")


allocation_system = AllocationSystem()

def get_allocation_system():
    return allocation_system

if __name__ == '__main__':
    asyncio.run(test())
    
