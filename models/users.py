from pydantic import BaseModel, Field
from typing import Optional
from .repository import AbstractModel, PyObjectId

class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: str = Field(...)


class UserModel(AbstractModel):
    @property
    def collection(self):
        return 'users'

    username: str
    email: str = Field(...)
    full_name: str = Field(...)
    disabled: bool = Field(...)

class UserInDB(UserModel):
    id: Optional[PyObjectId] = Field(alias="_id", default=None)
    hashed_password: str = Field(...)

class UserCreate(UserModel):
    password: str = Field(...)

    def to_userdb(self, hashed_password: str) -> UserInDB:
        return UserInDB(
            username=self.username,
            email=self.email,
            full_name=self.full_name,
            disabled=False,
            hashed_password=hashed_password
        )
