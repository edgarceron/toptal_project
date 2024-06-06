import os
from typing import Optional, List
from fastapi import FastAPI, Body, status
import motor.motor_asyncio
from pydantic import ConfigDict, BaseModel, Field, EmailStr

from models.students import ApartmentModel, ApartmentCollection
MONGODB_URL = "mongodb://root:example@127.0.0.1:27017"
app = FastAPI()
client = motor.motor_asyncio.AsyncIOMotorClient(MONGODB_URL)
db = client.get_database("renting")
apartment_collection = db.get_collection("apartments")

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
    new_apartment = await apartment_collection.insert_one(
        apartment.model_dump(by_alias=True, exclude=["id"])
    )
    created_apartment = await apartment_collection.find_one(
        {"_id": new_apartment.inserted_id}
    )
    return created_apartment