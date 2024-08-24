from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from db.database import get_db
from db.models import AgencyModel
from schemas.Agency import Agency
from routers.agency_router import router as agency_router
from routers.donation_router import router as donation_router
from routers.donor_router import router as donor_router
from uuid import uuid4

app = FastAPI()

# Include routers
app.include_router(agency_router, prefix="/api", tags=["agencies"])
app.include_router(donation_router, prefix="/api", tags=["donations"])
app.include_router(donor_router, prefix="/api", tags=["donors"])

@app.get("/health")
async def health():
    return {"message": "Algorithm service is up and running!"}