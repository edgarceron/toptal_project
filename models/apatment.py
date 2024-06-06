
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
    

class ApartmentCollection(BaseModel):
    apartments: List[ApartmentModel]

