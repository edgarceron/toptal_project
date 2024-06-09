import abc
from uuid import uuid4
from pydantic import BaseModel, Field
import motor.motor_asyncio
from motor.motor_gridfs import AgnosticGridFSBucket
from bson import ObjectId
from typing import Optional
from typing_extensions import Annotated
from pydantic.functional_validators import BeforeValidator
from pymongo import ReturnDocument

PyObjectId = Annotated[str, BeforeValidator(str)]

class AbstractModel(BaseModel):
    @property
    @abc.abstractmethod
    def collection(self):
        ...

class FileModel(AbstractModel):
    @property
    def collection(self):
        return 'files' 
    id: Optional[PyObjectId] = Field(alias="_id", default=None)
    data: bytes


class AbstractRepository(abc.ABC):
    @abc.abstractmethod
    def add(self, model: AbstractModel):
        raise NotImplementedError



class MongoConnection:
    MONGODB_URL = "mongodb://root:example@127.0.0.1:27017"        
    def __init__(self, collection):
        self.client = motor.motor_asyncio.AsyncIOMotorClient(self.MONGODB_URL)
        self.db = self.client.get_database("renting")
        self.collection = self.db.get_collection(collection)
    
    async def __aenter__(self):
        return self.collection
    
    async def __aexit__(self, exc_type, exc, tb):
        self.client.close()

class MongoGridFSConnection:
    MONGODB_URL = "mongodb://root:example@127.0.0.1:27017"        
    def __init__(self):
        self.client = motor.motor_asyncio.AsyncIOMotorClient(self.MONGODB_URL)
        self.db = self.client.get_database("images")
    
    async def __aenter__(self) -> AgnosticGridFSBucket:
        self.fs = motor.motor_asyncio.AsyncIOMotorGridFSBucket(self.db)
        return self.fs
    
    async def __aexit__(self, exc_type, exc, tb):
        self.client.close()


class MongoRepository(AbstractRepository):

    async def add(self, model: AbstractModel) -> AbstractModel:
        async with MongoConnection(model.collection) as collection:
            new = await collection.insert_one(
                model.model_dump(by_alias=True, exclude=["id"])
            )
            created = await collection.find_one(
                {"_id": new.inserted_id}
            )
        return created

    async def get(self, id: str, collection_type: str) -> Optional[dict]:
        async with MongoConnection(collection_type) as collection:
            model = await collection.find_one({"_id": ObjectId(id)})
        return model
    
    async def get_by_field(self, match: str, collection_type: str, field: str) -> Optional[dict]:
        async with MongoConnection(collection_type) as collection:
            model = await collection.find_one({field: match})
        return model
    
    async def delete(self, id: str, collection_type: str):
        async with MongoConnection(collection_type) as collection:
            delete_result = await collection.delete_one({"_id": ObjectId(id)})
        return delete_result.deleted_count
    
    async def find_one_and_update(self, id: str, model: AbstractModel) -> Optional[dict]:
        updates = {
            k: v for k, v in model.model_dump(by_alias=True).items() if v is not None
        }
        if len(updates) == 0: 
            return None
        async with MongoConnection(model.collection) as collection:
            update_result = await collection.find_one_and_update(
                {"_id": ObjectId(id)},
                {"$set": updates},
                return_document=ReturnDocument.AFTER,
            )
            return update_result

    async def filter(collection_type: str, query: dict, page: int, per_page: int = 100):
        offset = (page - 1) * per_page
        async with MongoConnection(collection_type) as collection:
            result = await collection.find(query).skip(offset).limit(per_page)
        return result.to_list()


class GridFSRepository(AbstractRepository):
    async def add(self, model: FileModel) -> ObjectId:
        async with MongoGridFSConnection() as fs:
            file_id = await fs.upload_from_stream(
                str(uuid4()),
                model.data)
            return file_id

    async def get(self, id: str) -> FileModel:
        async with MongoGridFSConnection() as fs:
            print("Reading")
            print(id)
            grid_out = await fs.open_download_stream(ObjectId(id))
            contents = await grid_out.read()
            return FileModel(
                id=ObjectId(id),
                data=contents
            )

    async def delete(self, id: str) -> int:
        async with MongoGridFSConnection() as fs:
            await fs.delete(ObjectId(id))
            