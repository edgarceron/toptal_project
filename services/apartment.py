
from ..models import apartments
from uuid import UUID
from ..models.repository import MongoRepository, GridFSRepository, FileModel
from ..security.auth import Hashing

class AparmentService():
    @staticmethod
    def _get_file_model(image: bytes):
        file_name = UUID(bytes=image)
        file = FileModel(
            file_name=file_name,
            data=image
        )
        return file

    @staticmethod
    async def create_apartment(apartment: apartments.ApartmentInput, user_name: str):
        repository = MongoRepository()
        file_repository = GridFSRepository()
        file = AparmentService._get_file_model(apartment.image)
        file_repository.add(file)

        created_apartment = await repository.add(apartment.to_apartment_in_db(user_name, file.file_name))
        response_apartment = apartments.ApartmentModel(**created_apartment)
        return response_apartment
    
    @staticmethod
    async def update_apartment(id: str, user_name: str, apartment: apartments.ApartmentUpdate):
        repository = MongoRepository()
        existing = await repository.get(id=id, collection_type=apartment.collection)
        if not existing or existing.get("realtor") != user_name:
            return None
        if apartment.image is not None:
            file_repository = GridFSRepository()
            file = AparmentService._get_file_model(apartment.image)
            file_repository.add(file)
            apartment.image_name = file.file_name
        del apartment.image
        updated_apartment = await repository.find_one_and_update(
            id=id,
            model=apartment
        )
        if updated_apartment is not None:
            return updated_apartment
        return existing
        
        
        
        
        


        
    