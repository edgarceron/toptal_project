
from datetime import datetime
from enum import Enum
from pydantic import BaseModel, Field, field_validator
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

    @field_validator('radius')
    def validate_radius(cls, value):
        if value <= 0:
            raise ValueError('radius must be a positive number')
        return value

    @field_validator('lat')
    def validate_lat(cls, value):
        if not (-90 <= value <= 90):
            raise ValueError('lat must be between -90 and 90')
        return value

    @field_validator('lon')
    def validate_lon(cls, value):
        if not (-180 <= value <= 180):
            raise ValueError('lon must be between -180 and 180')
        return value

    @field_validator('page')
    def validate_page(cls, value):
        if value <= 0:
            raise ValueError('page must be a positive integer')
        return value


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

    @field_validator('title', 'description')
    def validate_non_empty(cls, value: str, field):
        if not value or not value.strip():
            raise ValueError(f'{field.name} must not be empty')
        return value

    @field_validator('location')
    def validate_location(cls, value):
        if not isinstance(value, dict):
            raise ValueError('location must be a dictionary')
        if value.get('type') != 'Point':
            raise ValueError('location type must be "Point"')
        coordinates = value.get('coordinates')
        if not isinstance(coordinates, list) or len(coordinates) != 2:
            raise ValueError('location coordinates must be a list of two elements')
        lon, lat = coordinates
        if not (-180 <= lon <= 180):
            raise ValueError('longitude must be between -180 and 180')
        if not (-90 <= lat <= 90):
            raise ValueError('latitude must be between -90 and 90')
        return value

    @field_validator('price')
    def validate_price(cls, value):
        if value <= 0:
            raise ValueError('price must be a positive number')
        return value

    @field_validator('bedrooms')
    def validate_bedrooms(cls, value):
        if value <= 0:
            raise ValueError('bedrooms must be a positive integer')
        return value

    @field_validator('dateadded')
    def validate_date(cls, value):
        try:
            datetime.fromisoformat(value)
        except ValueError:
            raise ValueError('dateadded must be in a valid ISO 8601 format')
        return value

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

