from bson import ObjectId

from fastapi import APIRouter, Depends, HTTPException, status
from pymongo.database import Database

from dependencies import get_database
from models.users import User, Role
from services import userServices

router = APIRouter(prefix="/admin", tags=['admin'])


@router.post("/promote/{user_id}", response_model=User)
async def promote_user_to_superuser(
    user_id: str,
    db: Database = Depends(get_database),
    current_user: User = Depends(userServices.get_current_active_superuser)
):
    """
    Admins only. Promote a user to superuser.
    """
    user = userServices.get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    if user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="User is already an admin")

    db.users.update_one({"_id": ObjectId(user_id)}, {
                        "$set": {"is_superuser": True}})

    updated_user = userServices.get_user_by_id(db, user_id)
    return updated_user


@router.post("/verify-donor/{user_id}", response_model=User)
async def verify_donor(
    user_id: str,
    db: Database = Depends(get_database),
    current_user: User = Depends(userServices.get_current_active_superuser)
):
    """
    Admins only. Verify a donor.
    """
    user = userServices.get_user_by_id(db, user_id)
    print("ver", user.role)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    if user.role != Role.donor:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Only donors can be verified")

    db.users.update_one({"_id": ObjectId(user_id)}, {
                        "$set": {"is_verified": True}})

    updated_user = userServices.get_user_by_id(db, user_id)
    return updated_user
