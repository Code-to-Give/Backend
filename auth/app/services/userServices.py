import bcrypt
import jwt
import os

from bson import ObjectId
from typing import Dict, Any, Annotated
from datetime import datetime, timedelta, timezone
from fastapi import HTTPException, status, Depends
from fastapi.security import OAuth2PasswordBearer
from pymongo.database import Database

from models.users import UserRegister, UserLogin, User, Role


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/users/login")


ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")
JWT_REFRESH_SECRET_KEY = os.getenv("JWT_REFRESH_SECRET_KEY")


def create_user(db: Database, user: UserRegister) -> Dict[str, Any]:
    """
    Create a user using DI
    """
    if db.users.find_one({"email": user.email}):
        return {"success": False, "error": "Email already registered"}

    hashed_password = bcrypt.hashpw(
        user.password.get_secret_value().encode('utf-8'), bcrypt.gensalt())

    if user.role != Role.donor:
        is_verified = True
    else:
        is_verified = False

    user = {
        "email": user.email,
        "password": hashed_password.decode('utf-8'),
        "company_name": user.company_name,
        "name": user.name,
        "phone_number": user.phone_number,
        "role": user.role,
        "is_verified": is_verified,
        "is_superuser": False
    }

    try:
        result = db.users.insert_one(user)
    except Exception as e:
        return {"success": False, "error": f"Failed to create user: {str(e)}"}

    return {"success": True, "id": str(result.inserted_id), "message": "User created successfully"}


def get_user_by_id(db: Database, id: str) -> User:
    """
    Retrieve a user by ID.
    """
    user = db.users.find_one({"_id": ObjectId(id)})

    if not user:
        return False

    user["_id"] = str(user["_id"])

    return User(**user)


def authenticate_user(db: Database, user_login: UserLogin):
    """
    Authenticate a user by email and password.
    """
    user = db.users.find_one({"email": user_login.email})

    if not user:
        return False

    if not bcrypt.checkpw(user_login.password.get_secret_value().encode('utf-8'), user["password"].encode('utf-8')):
        return False

    user["_id"] = str(user["_id"])

    return User(**user)


def create_access_token(data: dict):
    expire = datetime.now(timezone.utc) + \
        timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode = {k: str(v) if isinstance(v, ObjectId)
                 else v for k, v in data.items()}
    to_encode.update({"exp": expire})

    encoded_jwt = jwt.encode(
        to_encode,
        JWT_SECRET_KEY,
        algorithm=ALGORITHM)
    return encoded_jwt


def create_refresh_token(data: dict) -> str:
    expire = datetime.now(timezone.utc) + \
        timedelta(minutes=REFRESH_TOKEN_EXPIRE_MINUTES)

    to_encode = {k: str(v) if isinstance(v, ObjectId)
                 else v for k, v in data.items()}
    to_encode.update({"exp": expire})

    encoded_jwt = jwt.encode(
        to_encode, JWT_REFRESH_SECRET_KEY, ALGORITHM)
    return encoded_jwt


async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]) -> User:
    """
    Retrieve the current user from the JWT token.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(token, JWT_SECRET_KEY,
                             algorithms=[ALGORITHM])
        print(payload)
        return User(**payload)

    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except jwt.InvalidTokenError:
        raise credentials_exception


async def get_current_active_user(
    current_user: Annotated[User, Depends(get_current_user)],
):
    """
    Ensure the current user is active.
    """
    if current_user.role == Role.donor and not current_user.is_verified:
        raise HTTPException(
            status_code=400, detail="Your account has not been verified")
    return current_user


async def get_current_active_superuser(
    current_user: Annotated[User, Depends(get_current_user)],
):
    """
    Ensure the current user is active.
    """
    if not current_user.is_superuser:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="Insufficient permissions")
    return current_user
