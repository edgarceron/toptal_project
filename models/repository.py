import abc
from pydantic import BaseModel
import motor.motor_asyncio
from bson import ObjectId
from typing_extensions import Annotated
from pydantic.functional_validators import BeforeValidator

PyObjectId = Annotated[str, BeforeValidator(str)]

class AbstractModel(BaseModel):
    @property
    @abc.abstractmethod
    def collection(self):
        ...


class AbstractRepository(abc.ABC):
    @abc.abstractmethod  #(1)
    def add(self, model: AbstractModel):
        raise NotImplementedError  #(2)

    @abc.abstractmethod
    def get(self, id: ObjectId) -> AbstractModel:
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

    async def get(self, id: str, collection_type: str) -> AbstractModel:
        async with MongoConnection(collection_type) as collection:
            model = await collection.find_one({"_id": ObjectId(id)})
        return model
    
    async def delete(self, id: str, collection_type: str):
        async with MongoConnection(collection_type) as collection:
            delete_result = await collection.delete_one({"_id": ObjectId(id)})
        return delete_result.deleted_count



