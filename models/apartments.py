
from enum import Enum
from pydantic import BaseModel, Field
from typing import Optional, List
from .repository import AbstractModel, PyObjectId

class RadiusUnit(Enum):
    km = "km"
    mi = "mi"

class GeospatialApartmentSearch(BaseModel):
    radius: float = Field(...)
    lat: float = Field(...)
    lon: float = Field(...)
    radius_unit: RadiusUnit = Field(...)
    page: int = Field(...)


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
    image_id: Optional[str] = Field(default=None)


class ApartmentInDB(ApartmentModel):
    image_id: str = Field(...)
    realtor: str = Field(...)

class ApartmentInput(ApartmentModel):
    image: bytes = Field(...)

    def to_apartment_in_db(self, user_name: str, image_id: str):
        return ApartmentInDB(
            title=self.title,
            description=self.description,
            location =self.location ,
            price=self.price,
            bedrooms=self.bedrooms,
            dateadded=self.dateadded,
            image_id=image_id,
            realtor=user_name
        )


class ApartmentCollection(BaseModel):
    apartments: List[ApartmentInDB]

