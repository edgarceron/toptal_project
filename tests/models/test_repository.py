import pytest
from ...models import repository
from pydantic import Field
from typing import Optional

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

@pytest.mark.asyncio
async def test_add(mock_model: MyModel):
    repo = repository.MongoRepository()
    result = await repo.add(mock_model)
    print(result)
    assert result is not None
    await repo.delete(mock_model.id, mock_model.collection)