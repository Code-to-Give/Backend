from fastapi import FastAPI, Depends, HTTPException, WebSocket, WebSocketDisconnect
from contextlib import asynccontextmanager
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from db.database import get_db
from db.models import AgencyModel
from schemas.Agency import Agency
from routers.agency_router import router as agency_router
from routers.donation_router import router as donation_router
from routers.donor_router import router as donor_router
from routers.requirement_router import router as requirement_router
from uuid import uuid4
from AllocationSystem import get_allocation_system


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    async for db in get_db():
        allocation_system = await get_allocation_system(db)
        app.state.allocation_system = allocation_system
        app.state.db = db
        break  # We only need one database session for initialization
    yield
    # Shutdown
    if hasattr(app.state, 'db'):
        await app.state.db.close()

app = FastAPI(lifespan=lifespan)


app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("CORS_ORIGINS", "*").split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(agency_router, prefix="/api", tags=["agencies"])
app.include_router(donation_router, prefix="/api", tags=["donations"])
app.include_router(donor_router, prefix="/api", tags=["donors"])
app.include_router(requirement_router,prefix="/api", tags=["requirements"])

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
