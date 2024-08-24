from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from db.database import get_db  
from db.models import AgencyModel 
from schemas.Agency import Agency
from uuid import uuid4

app = FastAPI()

@app.post("/agencies/")
def create_agency(agency: Agency, db: Session = Depends(get_db)):
    db_agency = AgencyModel(
        id=str(uuid4()),
        name=agency.name,
        requirements=agency.requirements,
        priority_flag=agency.priority_flag,
        location=agency.location
    )
    db.add(db_agency)
    db.commit()
    db.refresh(db_agency)
    return {"id": db_agency.id, "name": db_agency.name, "message": "Agency created successfully"}

@app.get("/agencies/{agency_id}")
def read_agency(agency_id: str, db: Session = Depends(get_db)):
    db_agency = db.query(AgencyModel).filter(AgencyModel.id == agency_id).first()
    if db_agency is None:
        raise HTTPException(status_code=404, detail="Agency not found")
    return {
        "id": db_agency.id,
        "name": db_agency.name,
        "requirements": db_agency.requirements,
        "priority_flag": db_agency.priority_flag,
        "location": db_agency.location
    }   

@app.get("/health")
async def health():
    return {"message": "Algorithm service is up and running!"}
