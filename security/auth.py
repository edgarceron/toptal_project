import jwt
from datetime import datetime, timedelta, timezone
from typing import Annotated, Final, Optional
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jwt.exceptions import InvalidTokenError
from passlib.context import CryptContext
from ..models import users
from ..models.repository import MongoRepository

SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

app = FastAPI()

class Hashing:
    PWD_CONTEXT = CryptContext(schemes=["bcrypt"], deprecated="auto")

    @staticmethod
    def verify_password(plain_password, hashed_password):
        return Hashing.PWD_CONTEXT.verify(plain_password, hashed_password)

    @staticmethod
    def get_password_hash(password):
        return Hashing.PWD_CONTEXT.hash(password)


class Auth:
    ACCESS_TOKEN_EXPIRE_MINUTES: Final[int] = 30
    
    @staticmethod
    async def get_user(username: str) -> users.UserInDB:
        repo = MongoRepository()
        user_dict = await repo.get_by_field(match=username, collection_type='users', field='username')
        result = users.UserInDB(**user_dict)
        return result

    @staticmethod
    async def authenticate_user(username: str, password: str) -> Optional[users.UserInDB]:
        user = await Auth.get_user(username)
        if not user:
            return False
        if not Hashing.verify_password(password, user.hashed_password):
            return False
        return user

    @staticmethod
    async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]) -> users.UserInDB:
        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            username: str = payload.get("sub")
            if username is None:
                raise credentials_exception
            token_data = users.TokenData(username=username)
        except InvalidTokenError:
            raise credentials_exception
        user = await Auth.get_user(username=token_data.username)
        if user is None:
            raise credentials_exception
        return user


    @staticmethod
    def create_access_token(data: dict):
        expires_delta = Auth.access_token_expires()
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.now(timezone.utc) + expires_delta
        else:
            expire = datetime.now(timezone.utc) + timedelta(minutes=15)
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt
    
    @staticmethod
    def access_token_expires():
        return timedelta(minutes=Auth.ACCESS_TOKEN_EXPIRE_MINUTES)

    @staticmethod
    async def get_current_active_user(
        current_user: Annotated[users.UserInDB, Depends(get_current_user)],
    ):
        aw = await current_user
        if aw.disabled:
            raise HTTPException(status_code=400, detail="Inactive user")
        return aw



    