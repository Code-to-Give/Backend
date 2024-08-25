from fastapi import APIRouter, Depends, HTTPException, status
from pymongo.database import Database

from dependencies import get_database
from models.users import User, UserRegister, Token, UserLogin
from services import userServices

router = APIRouter(prefix="/api/users", tags=['users'])


@router.post("/", response_model=User, status_code=status.HTTP_201_CREATED)
async def register_user(user_create: UserRegister, db: Database = Depends(get_database)):
    """
    Controller to register a new user.
    Calls the create_user service and handles the response.
    """
    response = userServices.create_user(db, user_create)

    if not response["success"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=response["error"])

    return {
        "id": response["id"],
        "email": user_create.email,
        "company_name": user_create.company_name,
        "name": user_create.name,
        "phone_number": user_create.phone_number,
        "role": user_create.role,
        "is_verified": False,
        "is_superuser": False
    }


@router.post("/login")
async def login(user_login: UserLogin, db: Database = Depends(get_database)):
    """
    Authenticate a user by their email and password.
    """
    user = userServices.authenticate_user(db, user_login)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = userServices.create_access_token(user)

    return Token(access_token=access_token, token_type="Bearer")


@router.get("/me", response_model=User)
async def get_me(current_user: User = Depends(userServices.get_current_user)):
    """
    Controller to get the current authenticated user's information.
    """

    return current_user
