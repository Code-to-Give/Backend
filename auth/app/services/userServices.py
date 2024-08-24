from pymongo.database import Database
from models.users import UserRegister, UserLogin
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
        "email": user.email,
        "password": hashed_password.decode('utf-8'),
        "company_name": user.company_name,
        "name": user.name,
        "phone_number": user.phone_number,
        "role": user.role
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
            "email": user["email"],
            "is_verified": user.get("is_verified", False),
            "company_name": user["company_name"],
            "name": user["name"],
            "phone_number": user["phone_number"],
            "role": user["role"]
        }
    }


def authenticate_user(db: Database, user_login: UserLogin) -> Dict[str, Any]:
    """
    Authenticate a user by email and password.
    """
    user = db.users.find_one({"email": user_login.email})

    if not user:
        return {"success": False, "error": "User not found"}

    if not bcrypt.checkpw(user_login.password.encode('utf-8'), user["password"].encode('utf-8')):
        return {"success": False, "error": "Invalid password"}

    return {
        "success": True,
        "user": {
            "user_id": str(user["_id"]),
            "email": user["email"],
            "role": user["role"],
            "is_verified": user.get("is_verified", False),
            "company_name": user["company_name"],
            "name": user["name"],
            "phone_number": user["phone_number"],
            "role": user["role"]
        }
    }
