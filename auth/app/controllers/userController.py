from pymongo.database import Database
from models.users import UserRegister, User
import bcrypt
from bson import ObjectId

from typing import Dict, Any


def create_user(db: Database, user: UserRegister) -> Dict[str, Any]:
    """
    Create a user using DI
    """
    if db.users.find_one({"email": user.email}):
        return {"success": False, "error": "Email already registered"}

    hashed_password = bcrypt.hashpw(
        user.password.get_secret_value().encode('utf-8'), bcrypt.gensalt())

    user = {
        "full_name": user.full_name,
        "email": user.email,
        "password": hashed_password.decode('utf-8')
    }

    try:
        result = db.users.insert_one(user)
    except Exception as e:
        return {"success": False, "error": f"Failed to create user: {str(e)}"}

    return {"success": True, "user_id": str(result.inserted_id), "message": "User created successfully"}


def get_user_by_id(db: Database, user_id: str):
    """
    Retrieve a user by ID.
    """
    user = db.users.find_one({"_id": ObjectId(user_id)})

    if not user:
        return {"success": False, "error": "User not found"}

    return {
        "success": True,
        "user": {
            "id": str(user["_id"]),
            "full_name": user.get("full_name"),
            "email": user["email"],
            "is_verified": user.get("is_verified", False),
            "is_superuser": user.get("is_superuser", False),
        }
    }
