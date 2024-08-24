import os
from dotenv import load_dotenv

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi

from routes.userRoutes import router as user_router
from routes.adminRoutes import router as admin_router

load_dotenv()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("CORS_ORIGINS", "*").split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event('startup')
def startup_db_client():
    mongodb_uri = os.getenv('MONGODB_URI')
    db_name = os.getenv('AUTH_DB_NAME')

    if not mongodb_uri or not db_name:
        raise ValueError(
            "MONGODB_URI and DB_NAME must be set in the environment variables.")

    # Create a new client and connect to the server
    app.mongodb_client = MongoClient(mongodb_uri, server_api=ServerApi('1'))
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
app.include_router(admin_router)
