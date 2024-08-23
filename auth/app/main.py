import os

from fastapi import FastAPI
from dotenv import load_dotenv

from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi

from routes.userRoutes import router as user_router

load_dotenv()

app = FastAPI()


@app.on_event('startup')
def startup_db_client():
    mongodb_uri = os.getenv('MONGODB_URI')
    db_name = os.getenv('DB_NAME')

    if not mongodb_uri or not db_name:
        raise ValueError(
            "MONGODB_URI and DB_NAME must be set in the environment variables.")

    # Create a new client and connect to the server
    app.mongodb_client = MongoClient(mongodb_uri)
    app.database = app.mongodb_client[db_name]

    # Send a ping to confirm a successful connection
    try:
        app.mongodb_client.admin.command('ping')
        print("Pinged your deployment. You successfully connected to MongoDB!")
    except Exception as e:
        print(e)


@app.on_event("shutdown")
def shutdown_db_client():
    app.mongodb_client.close()


@app.get("/health")
async def health():
    return {"message": "Authentication service is up and running!"}

app.include_router(user_router)
