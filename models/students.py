from typing_extensions import Annotated
from pydantic.functional_validators import BeforeValidator
from pydantic import ConfigDict, BaseModel, Field
from typing import Optional, List, Union

# Represents an ObjectId field in the database.
# It will be represented as a `str` on the model so that it can be serialized to JSON.
PyObjectId = Annotated[str, BeforeValidator(str)]


class ApartmentModel(BaseModel):
    """
    Container for a single apartment record.
    """
    id: Optional[PyObjectId] = Field(alias="_id", default=None)
    title: str = Field(...)
    description: str = Field(...)
    location : dict = Field(...)
    price: float = Field(...)
    bedrooms: int = Field(...)
    dateadded: str = Field(...)

class ApartmentCollection(BaseModel):
    apartments: List[ApartmentModel]

