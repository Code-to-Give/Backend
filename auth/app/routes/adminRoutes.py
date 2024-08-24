from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from pymongo.database import Database

from dependencies import get_database
from models.users import User, UserRegister, UserUpdate, UpdatePassword, UserLogin
from Backend.auth.app.services.userServices import create_user, get_user_by_id

router = APIRouter(prefix="/admin", tags=['admin'])


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
        "email": user_create.email,
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


@router.put("/{user_id}")
async def update_user_info(user_id: str, updates: UserUpdate, db: Database = Depends(get_database)):
    pass


@router.post("/login")
async def login(user_login: UserLogin, db: Database = Depends(get_database)):
    pass

# @router.put("/{}")
# async def update_password(update_password: UpdatePassword, current_user: CurrentUser, db: Database = Depends(get_database)):
#     pass
