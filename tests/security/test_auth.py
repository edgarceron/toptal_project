import jwt
import pytest
from datetime import datetime, timedelta, timezone
from ...security.auth import Auth
from ...security.hashing import Hashing
from ...models import users
from ...services.users import UserService
from fastapi import HTTPException


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

@pytest.fixture
def mock_invalid_user():
    return None

@pytest.fixture
def token(mock_user: users.UserInDB):
    data = {"sub": mock_user.user_name}
    return Auth.create_access_token(data)

@pytest.fixture
async def setup_user_service(mock_user, mock_invalid_user, monkeypatch):
    async def mock_get_user(username: str):
        if username == "testuser":
            return mock_user
        else:
            return mock_invalid_user

    monkeypatch.setattr(UserService, "get_user", mock_get_user)


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

@pytest.mark.asyncio
async def test_should_authenticate_user_return_user_when_correct(mock_user: users.UserInDB, setup_user_service):
    await setup_user_service
    user = await Auth.authenticate_user("testuser", "testpassword")
    assert user == mock_user

@pytest.mark.asyncio
async def test_should_authenticate_user_return_false_when_incorrect(setup_user_service):
    await setup_user_service
    user = await Auth.authenticate_user("testuser", "wrongpassword")
    assert user is False

@pytest.mark.asyncio
async def test_should_get_current_user_return_user_when_is_auth(token: str, mock_user: users.UserInDB, setup_user_service):
    await setup_user_service
    user = await Auth.get_current_user(token)
    assert user.user_name == mock_user.user_name

@pytest.mark.asyncio
async def test_should_get_current_user_raise_error_when_is_not_auth(setup_user_service):
    await setup_user_service
    with pytest.raises(HTTPException) as exc_info:
        await Auth.get_current_user("invalidtoken")
    assert exc_info.value.status_code == 401

@pytest.mark.asyncio
async def test_should_get_current_user_raise_error_when_token_is_expired(mock_user: users.UserInDB, setup_user_service):
    await setup_user_service
    data = {"sub": mock_user.user_name, "exp": datetime.now(timezone.utc) - timedelta(minutes=1)}
    expired_token = jwt.encode(data, Auth.SECRET_KEY, algorithm=Auth.ALGORITHM)
    with pytest.raises(HTTPException) as exc_info:
        await Auth.get_current_user(expired_token)
    assert exc_info.value.status_code == 401