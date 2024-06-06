from pydantic import BaseModel, Field
from .repository import AbstractModel


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
    hashed_password: str = Field(...)



