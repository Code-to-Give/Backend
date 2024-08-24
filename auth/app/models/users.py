from enum import Enum
from uuid import uuid4, UUID
from typing import Optional
from datetime import datetime


from pydantic import BaseModel, Field, SecretStr, EmailStr
from pydantic_extra_types.phone_numbers import PhoneNumber


class Role(str, Enum):
    donor = "Donor"
    beneficiary = "Beneficiary"


class UserBase(BaseModel):
    email: EmailStr = Field(max_length=255)
    is_verified: bool = False
    is_superuser: bool = False
    company_name: str = Field(max_length=255)
    name: str = Field(max_length=255)
    phone_number: PhoneNumber = Field()
    role: Optional[Role] = Field(None)


class UserRegister(BaseModel):
    email: EmailStr = Field(max_length=255)
    password: SecretStr = Field(min_length=8, max_length=40)
    company_name: str = Field(max_length=255)
    name: str = Field(max_length=255)
    phone_number: PhoneNumber = Field()
    role: Optional[Role] = Field(None)


class UserLogin(BaseModel):
    email: EmailStr = Field(max_length=255)
    password: SecretStr = Field(min_length=8, max_length=40)


class UserUpdate(BaseModel):
    company_name: Optional[str] = Field(None, max_length=255)
    name: Optional[str] = Field(None, max_length=255)
    phone_number: Optional[PhoneNumber] = Field(None)


class UpdatePassword(BaseModel):
    current_password: str = Field(min_length=8, max_length=40)
    new_password: str = Field(min_length=8, max_length=40)


class User(UserBase):
    id: UUID = Field(default_factory=uuid4, alias="_id")

    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    sub: UUID = Field(..., description="The unique identifier for the user")
    email: EmailStr = Field(..., description="The user's email address")
    role: Optional[Role] = Field(None, description="The user's role")
    is_verified: bool = Field(..., description="Whether the user is verified")
    is_superuser: bool = Field(...,
                               description="Whether the user has superuser privileges")
    exp: datetime = Field(..., description="Expiration time of the token")
