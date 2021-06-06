from typing import Optional

from pydantic import BaseModel, EmailStr

from schemas.fields import TitleType, IdType, PasswordType


# Shared properties
class UserBase(BaseModel):
    email: Optional[EmailStr] = None
    is_active: Optional[bool] = True
    is_superuser: bool = False
    fullname: Optional[TitleType] = None


# Properties to receive via API on creation
class UserCreate(UserBase):
    email: EmailStr
    password: PasswordType
    fullname: Optional[TitleType] = None


# Properties to receive via API on update
class UserUpdate(UserBase):
    password: Optional[PasswordType] = None


class UserInDBBase(UserBase):
    id: Optional[IdType] = None

    class Config:
        orm_mode = True


# Additional properties to return via API
class User(UserInDBBase):
    pass


# Additional properties stored in DB
class UserInDB(UserInDBBase):
    hashed_password: PasswordType
