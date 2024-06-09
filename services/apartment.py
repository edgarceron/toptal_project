
from bson import ObjectId
from ..models import apartments
from ..models.repository import MongoRepository, GridFSRepository, FileModel
from ..security.auth import Hashing

class AparmentService():

    DEFAULT_COLLECTION = 'apartments'
    @staticmethod
    def _get_file_model(image: bytes):
        file = FileModel(
            data=image
        )
        return file

    @staticmethod
    async def create_apartment(apartment: apartments.ApartmentInput, user_name: str):
        repository = MongoRepository()
        file_repository = GridFSRepository()
        file = AparmentService._get_file_model(apartment.image)
        file_id = file_repository.add(file)

        created_apartment = await repository.add(apartment.to_apartment_in_db(user_name, file_id))
        response_apartment = apartments.ApartmentModel(**created_apartment)
        return response_apartment
    
    @staticmethod
    async def read_apartment(id: str):
        repository = MongoRepository()
        existing = await repository.get(id=id, collection_type=AparmentService.DEFAULT_COLLECTION)
        if not existing:
            return None
        else:
            return existing
    
    @staticmethod
    async def update_apartment(id: str, user_name: str, apartment: apartments.ApartmentUpdate):
        repository = MongoRepository()
        existing = await repository.get(id=id, collection_type=apartment.collection)
        if not existing or existing.get("realtor") != user_name:
            return None
        if apartment.image is not None:
            file_repository = GridFSRepository()
            file = AparmentService._get_file_model(apartment.image)
            file_id = file_repository.add(file)
            apartment.image_id = file_id
        del apartment.image
        updated_apartment = await repository.find_one_and_update(
            id=id,
            model=apartment
        )
        if updated_apartment is not None:
            return updated_apartment
        return existing
        
    @staticmethod
    async def delete_apartment(id: str, user_name: str) -> bool:
        repository = MongoRepository()
        file_repository = GridFSRepository()
        existing = await repository.get(id=id, collection_type=AparmentService.DEFAULT_COLLECTION)
        if not existing or existing.get("realtor") != user_name:
            return False
        apartment = apartments.ApartmentInDB(**existing)
        image_delete = file_repository.delete(apartment.image_id)
        apartment_delete = repository.delete(id, AparmentService.DEFAULT_COLLECTION)
        return bool(image_delete + apartment_delete)
    
    @staticmethod
    async def list_apartments(user_name: str, page: int) -> apartments.ApartmentCollection:
        repository = MongoRepository()
        results = await repository.filter(
            collection_type=AparmentService.DEFAULT_COLLECTION,
            query={"username": user_name},
            page=page
        )
        return apartments.ApartmentCollection(results)
    
    @staticmethod
    def _get_geo_query_dict(geo_search: apartments.GeospatialApartmentSearch):
        miles_to_meters = 1609.34
        kilometers_to_meters = 1000
        if geo_search.radius_unit == apartments.RadiusUnit.mi:
            radius_in_meters = geo_search.radius * miles_to_meters
        elif  geo_search.radius_unit == apartments.RadiusUnit.km:
            radius_in_meters = geo_search.radius * kilometers_to_meters
        else:
            raise ValueError("Unsupported unit. Use 'miles' or 'kilometers'.")
        query = {
            "location": {
                "$near": {
                    "$geometry": {
                        "type": "Point",
                        "coordinates": [geo_search.lon, geo_search.lat]
                    },
                    "$maxDistance": radius_in_meters
                }
            }
        }
        return query

    @staticmethod
    async def list_apartments_by_radius(
        geo_search: apartments.GeospatialApartmentSearch, 
    ) -> apartments.ApartmentCollection:
        repository = MongoRepository()
        query = AparmentService._get_geo_query_dict(geo_search)
        results = await repository.filter(
            collection_type=AparmentService.DEFAULT_COLLECTION,
            query=query,
            page=geo_search.page
        )
        return apartments.ApartmentCollection(results)
 