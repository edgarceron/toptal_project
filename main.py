
from fastapi import FastAPI, Body, status, Depends, HTTPException

from .models.apatment import ApartmentModel, ApartmentCollection
from .models.users import UserModel, UserCreate, Token, UserType
from .services.users import UserService
from .services.apartment import AparmentService
from .security.auth import Auth
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
    if current_user.user_type == UserType.realtor:
        created_apartment = AparmentService.create_apartment(apartment=apartment)
        return created_apartment
    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only realtor could create apartments"
        )

@app.post(
    "/user/",
    response_description="Add new student",
    response_model=UserModel,
    status_code=status.HTTP_201_CREATED,
    response_model_by_alias=False,
)
async def create_user(user: UserCreate = Body(...)):
    return UserService.create_user(user)

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

@app.get("/users/me/apartments/")
async def read_own_items(
    current_user: Annotated[UserModel, Depends(Auth.get_current_active_user)],
):
    return [{"item_id": "Foo", "owner": current_user.username}]