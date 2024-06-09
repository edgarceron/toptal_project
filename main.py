
from typing import Annotated
from fastapi import FastAPI, Body, status, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.responses import Response
from .models.apartments import ApartmentUpdate, ApartmentInput, ApartmentInDB, ApartmentCollection, GeospatialApartmentSearch
from .models.users import UserModel, UserCreate, Token, UserType
from .services.users import UserService
from .services.apartment import AparmentService
from .security.auth import Auth


MONGODB_URL = "mongodb://root:example@127.0.0.1:27017"
app = FastAPI()

@app.put("/apartments")
def read_root():
    return {"Hello": "World"}


@app.post(
    "/apartment/",
    response_description="Add new apartment",
    response_model=ApartmentInDB,
    status_code=status.HTTP_201_CREATED,
    response_model_by_alias=False,
)
async def create_apatment(
    current_user: Annotated[UserModel, Depends(Auth.get_current_active_user)],
    apartment: ApartmentInput = Body(...),
):
    if current_user.user_type == UserType.realtor:
        created_apartment = await AparmentService.create_apartment(apartment=apartment, user_name=current_user.user_name)
        return created_apartment
    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only realtor could create apartments"
        )

@app.patch(
    "/apartment/{id}",
    response_description="Update apartment",
    response_model=ApartmentInDB,
    status_code=status.HTTP_201_CREATED,
    response_model_by_alias=False,
)
async def update_apatment(
    current_user: Annotated[UserModel, Depends(Auth.get_current_active_user)],
    id: str,
    apartment: ApartmentUpdate = Body(...),
):
    if current_user.user_type == UserType.realtor:
        created_apartment = await AparmentService.update_apartment(id=id, user_name=current_user.user_name, apartment=apartment)
        return created_apartment
    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only realtor could create apartments"
        )

@app.get(
    "/apartment/{id}",
    response_description="Update apartment",
    response_model=ApartmentInDB,
    status_code=status.HTTP_201_CREATED,
    response_model_by_alias=False,
)
async def get_apatment(
    current_user: Annotated[UserModel, Depends(Auth.get_current_active_user)],
    id: str,
):
    if current_user is not None:
        apartment = await AparmentService.read_apartment(id)
        return apartment
    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only authenticated users could see apartments"
        )


@app.delete(
    "/apartment/{id}",
    response_description="Delete apartment"
)
async def delete_apatment(
    current_user: Annotated[UserModel, Depends(Auth.get_current_active_user)],
    id: str,
):
    if current_user is not None:
        delete_result = await AparmentService.delete_apartment(id, current_user.user_name)
        if delete_result:
            return Response(status_code=status.HTTP_204_NO_CONTENT)
    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only authenticated users could see apartments"
        )

@app.post(
    "/user/",
    response_description="Add new student",
    response_model=UserModel,
    status_code=status.HTTP_201_CREATED,
    response_model_by_alias=False,
)
async def create_user(user: UserCreate = Body(...)):
    return await UserService.create_user(user)

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
        data={"sub": user.user_name}
    )
    return Token(access_token=access_token, token_type="bearer")

@app.get("/users/me/", response_model=UserModel)
async def read_users_me(
    current_user: Annotated[UserModel, Depends(Auth.get_current_active_user)],
):
    return current_user

@app.get(
    "/users/me/apartments/{page}",
    response_model=ApartmentCollection,
    response_model_by_alias=False,
    response_description="Lisy my listed apartments",
)
async def read_own_items(
    current_user: Annotated[UserModel, Depends(Auth.get_current_active_user)],
    page: int = 1
):
    if current_user.user_type == UserType.realtor:
        return await AparmentService.list_apartments(current_user.user_name, page)
    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only realtor could list apartments"
        )
    

@app.post(
    "/search_apartments",
    response_model=ApartmentCollection,
    response_model_by_alias=False,
    response_description="Search apartment base on location and radius",
)
async def search_apartments(
    current_user: Annotated[UserModel, Depends(Auth.get_current_active_user)],
    geo_search: GeospatialApartmentSearch = Body(...),
):
    if current_user is not None:
        return await AparmentService.list_apartments_by_radius(geo_search=geo_search)
    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only authenticated users could see apartments"
        )
