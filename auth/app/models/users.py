from bson import ObjectId
import uuid
from pydantic import BaseModel, Field, SecretStr, EmailStr


class UserBase(BaseModel):
    email: EmailStr = Field(max_length=255)
    is_verified: bool = False
    is_superuser: bool = False
    full_name: str | None = Field(default=None, max_length=255)


class UserRegister(BaseModel):
    email: EmailStr = Field(max_length=255)
    password: SecretStr = Field(min_length=8, max_length=40)
    full_name: str | None = Field(default=None, max_length=255)


class User(UserBase):
    id: str = Field(default_factory=lambda: str(ObjectId()), alias="_id")

    class Config:
        orm_mode = True
