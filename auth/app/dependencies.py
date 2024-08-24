import os
# import jwt

from pymongo.mongo_client import MongoClient
from pymongo.database import Database
from fastapi import Depends


def get_mongo_client() -> MongoClient:
    mongodb_uri = os.getenv('MONGODB_URI')
    return MongoClient(mongodb_uri)


def get_database(client: MongoClient = Depends(get_mongo_client)) -> Database:
    db_name = os.getenv('AUTH_DB_NAME')
    return client[db_name]
