from enum import Enum
from typing import Optional
from bson import ObjectId

from pydantic import BaseModel, Field, EmailStr
from pydantic_extra_types.phone_numbers import PhoneNumber


class Role(str, Enum):
    donor = "Donor"
    beneficiary = "Beneficiary"


class UserBase(BaseModel):
    email: EmailStr = Field(max_length=255)
    is_verified: bool = False
    company_name: str = Field(max_length=255)
    name: str = Field(max_length=255)
    phone_number: PhoneNumber = Field()
    role: Role = Field()


class UserRegister(BaseModel):
    email: EmailStr = Field(max_length=255)
    password: str = Field(min_length=8, max_length=40)
    company_name: str = Field(max_length=255)
    name: str = Field(max_length=255)
    phone_number: PhoneNumber = Field()
    role: Role = Field()


class UserLogin(BaseModel):
    email: EmailStr = Field(max_length=255)
    password: str = Field(min_length=8, max_length=40)


class UserUpdate(BaseModel):
    company_name: Optional[str] = Field(None, max_length=255)
    name: Optional[str] = Field(None, max_length=255)
    phone_number: Optional[PhoneNumber] = Field(None)


class UpdatePassword(BaseModel):
    current_password: str = Field(min_length=8, max_length=40)
    new_password: str = Field(min_length=8, max_length=40)


class User(UserBase):
    id: str = Field(default_factory=lambda: str(ObjectId()), alias="_id")

    class Config:
        orm_mode = True


class UserAdmin(User):
    is_superuser: bool = False
