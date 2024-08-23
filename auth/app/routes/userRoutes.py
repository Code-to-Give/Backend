from typing import List

from fastapi import APIRouter, Depends, Request, HTTPException, status
from pymongo.database import Database

from dependencies import get_database
from models.users import User, UserRegister
from controllers.userController import create_user, get_user_by_id

router = APIRouter(prefix="/users", tags=['users'])


@router.post("/", response_model=User, status_code=status.HTTP_201_CREATED)
async def register_user(user_create: UserRegister, db: Database = Depends(get_database)):
    """
    Controller to register a new user.
    Calls the create_user service and handles the response.
    """
    response = create_user(db, user_create)

    if not response["success"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=response["error"])

    return {
        "id": response["user_id"],
        "full_name": user_create.full_name,
        "email": user_create.email,
        "is_verified": False,
        "is_superuser": False,
    }


@router.get("/{user_id}", response_model=User)
async def get_user(user_id: str, db: Database = Depends(get_database)):
    """
    Controller to get a user by ID.
    """
    response = get_user_by_id(db, user_id)

    if not response["success"]:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=response["error"])

    return response["user"]
