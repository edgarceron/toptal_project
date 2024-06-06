
from fastapi import FastAPI, Body, status, Depends, HTTPException

from .models.apatment import ApartmentModel, ApartmentCollection
from .models.users import UserModel, UserCreate, Token
from .models.repository import MongoRepository
from .security.auth import Auth, Hashing
from typing import Annotated
from fastapi.security import OAuth2PasswordRequestForm

MONGODB_URL = "mongodb://root:example@127.0.0.1:27017"
app = FastAPI()

@app.put("/apartments")
def read_root():
    return {"Hello": "World"}


@app.post(
    "/apartment/",
    response_description="Add new student",
    response_model=ApartmentModel,
    status_code=status.HTTP_201_CREATED,
    response_model_by_alias=False,
)
async def create_apatment(
    current_user: Annotated[UserModel, Depends(Auth.get_current_active_user)],
    apartment: ApartmentModel = Body(...),
    ):
    repository = MongoRepository()
    created_apartment = await repository.add(apartment)
    return created_apartment

@app.post(
    "/user/",
    response_description="Add new student",
    response_model=UserModel,
    status_code=status.HTTP_201_CREATED,
    response_model_by_alias=False,
)
async def create_user(user: UserCreate = Body(...)):
    repository = MongoRepository()
    user_in_db = user.to_userdb(hashed_password=Hashing.get_password_hash(user.password))
    created_user = await repository.add(user_in_db)
    response_user = UserModel(**created_user)
    return response_user

@app.post("/token")
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
) -> Token:
    auth_object = Auth()
    user = await auth_object.authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = auth_object.create_access_token(
        data={"sub": user.username}
    )
    return Token(access_token=access_token, token_type="bearer")

@app.get("/users/me/", response_model=UserModel)
async def read_users_me(
    current_user: Annotated[UserModel, Depends(Auth.get_current_active_user)],
):
    return current_user


@app.get("/users/me/items/")
async def read_own_items(
    current_user: Annotated[UserModel, Depends(Auth.get_current_active_user)],
):
    return [{"item_id": "Foo", "owner": current_user.username}]