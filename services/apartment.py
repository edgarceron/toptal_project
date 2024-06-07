
from ..models import apatment
from ..models.repository import MongoRepository
from ..security.auth import Hashing

class AparmentService():    
    @staticmethod
    async def create_apartment(apartment: apatment.ApartmentModel):
        repository = MongoRepository()
        created_apartment = await repository.add(apartment)
        response_apartment = apatment.ApartmentModel(**created_apartment)
        return response_apartment
    
    async def update_apartment(id: str, apartment: apatment.ApartmentModel):
        ...