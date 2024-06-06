
from fastapi import FastAPI, Body, status

from models.apatment import ApartmentModel, ApartmentCollection
from models.users import UserModel
from models.repository import MongoRepository
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
async def create_apatment(apartment: ApartmentModel = Body(...)):
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
async def create_user(user: UserModel = Body(...)):
    repository = MongoRepository()
    created_user = await repository.add(user)
    return created_user