from enum import Enum
from pydantic import BaseModel, Field, EmailStr, field_validator
from typing import Optional
from .repository import AbstractModel, PyObjectId

class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: str = Field(...)

class UserType(Enum):
    realtor = "realtor"
    regular = "regular"


class UserModel(AbstractModel):
    @property
    def collection(self):
        return 'users' 

    user_name: str
    email: EmailStr = Field(...)
    full_name: str = Field(...)
    disabled: bool = Field(...)
    user_type: UserType = Field(...)

class UserInDB(UserModel):
    id: Optional[PyObjectId] = Field(alias="_id", default=None)
    hashed_password: str = Field(...)
    user_type: str = Field(...)

    def to_user_model(self):
        return UserModel(**self.model_dump())


class UserCreate(UserModel):
    password: str = Field(...)

    @field_validator('user_name')
    def user_name_length(cls, value):
        if not (3 <= len(value) <= 50):
            raise ValueError('user_name must be between 3 and 50 characters')
        return value

    @field_validator('password')
    def password_complexity(cls, value):
        if len(value) < 8:
            raise ValueError('Password must be at least 8 characters long')
        if not any(char.isdigit() for char in value):
            raise ValueError('Password must contain at least one digit')
        if not any(char.isupper() for char in value):
            raise ValueError('Password must contain at least one uppercase letter')
        if not any(char.islower() for char in value):
            raise ValueError('Password must contain at least one lowercase letter')
        return value

    def to_userdb(self, hashed_password: str) -> UserInDB:
        return UserInDB(
            user_name=self.user_name,
            email=self.email,
            full_name=self.full_name,
            user_type=self.user_type.value,
            disabled=False,
            hashed_password=hashed_password
        )
