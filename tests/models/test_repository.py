import pytest
import uuid
from ...models import repository
from pydantic import Field
from typing import Optional
from bson.objectid import ObjectId

pytest_plugins = ('pytest_asyncio',)

class MyModel(repository.AbstractModel):
        @property
        def collection(self):
            return 'mock'
        id: Optional[repository.PyObjectId] = Field(alias="_id", default=None)
        someprop : str = Field(...)


@pytest.fixture
def mock_model():
    my_mock = MyModel(someprop="Someinfo")
    return my_mock

@pytest.fixture
def mock_file():
    my_file = repository.FileModel(
        data=b"Hello world"
    )
    return my_file

@pytest.mark.asyncio
async def test_add(mock_model: MyModel):
    repo = repository.MongoRepository()
    result = await repo.add(mock_model)
    print(result)
    assert result is not None
    await repo.delete(mock_model.id, mock_model.collection)

@pytest.mark.asyncio
async def test_add_file(mock_file: repository.FileModel):
    repo = repository.GridFSRepository()
    file_id = await repo.add(mock_file)
    file = await repo.get(str(file_id))
    assert file is not None
    assert file.data == mock_file.data
    await repo.delete(file_id)
