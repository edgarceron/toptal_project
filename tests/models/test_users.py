from ...models.users import UserCreate, UserType, UserInDB
import pytest
from pydantic import ValidationError

def test_to_user_db():
    user_create_data = {
        "user_name": "testuser",
        "email": "test@example.com",
        "full_name": "Test User",
        "user_type": UserType.realtor,
        "password": "testpassword",
        "disabled": False
    }
    user_create = UserCreate(**user_create_data)
    hashed_password = "hashedtestpassword"

    user_in_db = user_create.to_userdb(hashed_password)

    assert isinstance(user_in_db, UserInDB)
    assert user_in_db.hashed_password == hashed_password
    assert user_in_db.user_name == user_create_data["user_name"]
    assert user_in_db.email == user_create_data["email"]
    assert user_in_db.full_name == user_create_data["full_name"]
    assert user_in_db.user_type == user_create_data["user_type"].value
    assert user_in_db.disabled is False


def test_user_create_should_only_accept_realtor_or_regular():
    valid_data_realtor = {
        "user_name": "realtor_user",
        "email": "realtor@example.com",
        "full_name": "Realtor User",
        "user_type": UserType.realtor,
        "password": "realtorpassword",
        "disabled": False
    }

    valid_data_regular = {
        "user_name": "regular_user",
        "email": "regular@example.com",
        "full_name": "Regular User",
        "user_type": UserType.regular,
        "password": "regularpassword",
        "disabled": False
    }

    invalid_data = {
        "user_name": "invalid_user",
        "email": "invalid@example.com",
        "full_name": "Invalid User",
        "user_type": "invalid",
        "password": "invalidpassword",
        "disabled": False
    }

    user_realtor = UserCreate(**valid_data_realtor)
    user_regular = UserCreate(**valid_data_regular)

    assert user_realtor.user_type == UserType.realtor
    assert user_regular.user_type == UserType.regular

    with pytest.raises(ValidationError):
        UserCreate(**invalid_data)
