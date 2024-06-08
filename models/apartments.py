
from pydantic import ConfigDict, BaseModel, Field
from typing import Optional, List, Union
from .repository import AbstractModel, PyObjectId
# Represents an ObjectId field in the database.
# It will be represented as a `str` on the model so that it can be serialized to JSON.


class ApartmentModel(AbstractModel):
    """
    Container for a single apartment record.
    """
    @property
    def collection(self):
        return 'apartments'

    id: Optional[PyObjectId] = Field(alias="_id", default=None)
    title: str = Field(...)
    description: str = Field(...)
    location : dict = Field(...)
    price: float = Field(...)
    bedrooms: int = Field(...)
    dateadded: str = Field(...)

class ApartmentUpdate(AbstractModel):
    @property
    def collection(self):
        return 'apartments'

    title: Optional[str] = Field(...)
    description: Optional[str] = Field(...)
    location : Optional[dict] = Field(...)
    price: Optional[float] = Field(...)
    bedrooms: Optional[int] = Field(...)
    image: Optional[bytes] = Field(...)
    image_name: Optional[bytes] = Field(...)


class ApartmentInDB(ApartmentModel):
    image_name: str = Field(...)
    realtor: str = Field(...)

class ApartmentInput(ApartmentModel):
    image: bytes = Field(...)

    def to_apartment_in_db(self, user_name: str, image_name: str):
        return ApartmentInDB(
            title=self.title,
            description=self.description,
            location =self.location ,
            price=self.price,
            bedrooms=self.bedrooms,
            dateadded=self.dateadded,
            image_name=image_name,
            realtor=user_name
        )


class ApartmentCollection(BaseModel):
    apartments: List[ApartmentModel]

