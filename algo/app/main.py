from fastapi import FastAPI, Depends, HTTPException, WebSocket, WebSocketDisconnect
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from db.database import get_db
from db.models import AgencyModel
from schemas.Agency import Agency
from routers.agency_router import router as agency_router
from routers.donation_router import router as donation_router
from routers.donor_router import router as donor_router
from uuid import uuid4
from AllocationSystem import get_allocation_system

app = FastAPI()


# Include routers
app.include_router(agency_router, prefix="/api", tags=["agencies"])
app.include_router(donation_router, prefix="/api", tags=["donations"])
app.include_router(donor_router, prefix="/api", tags=["donors"])

allocation_system = get_allocation_system()

@app.websocket("/ws/{agency_id}")
async def websocket_endpoint(websocket: WebSocket, agency_id: str):
    await allocation_system.connect(websocket, agency_id)
    try:
        while True:
            data = await websocket.receive_json()
            print(f"Received message from agency {agency_id}: {data}")
    except WebSocketDisconnect:
        allocation_system.disconnect(agency_id)
        print(f"Agency {agency_id} disconnected.")

@app.get("/health")
async def health():
    return {"message": "Algorithm service is up and running!"}

# Function to get the AllocationSystem instance
def get_allocation_system():
    return allocation_system