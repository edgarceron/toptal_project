from ...models import users
from ...security.hashing import Hashing
import pytest

@pytest.fixture
def mock_user():
    return users.UserInDB(
        user_name="testuser",
        full_name="full_name",
        email="email",
        hashed_password=Hashing.get_password_hash("testpassword"),
        user_type=users.UserType.realtor,
        disabled=False,
    )

def test_should_get_password_hash_work():
    password = "testpassword"
    hashed = Hashing.get_password_hash(password)
    assert Hashing.verify_password(password, hashed) is True

@pytest.mark.asyncio
async def test_should_verify_password_pass_when_correct_password(mock_user: users.UserInDB):
    assert Hashing.verify_password("testpassword", mock_user.hashed_password) is True

@pytest.mark.asyncio
async def test_should_verify_password_fail_when_incorrect_password(mock_user: users.UserInDB):
    assert Hashing.verify_password("wrongpassword", mock_user.hashed_password) is False
