
from fastapi import HTTPException, status
from ..models import users
from ..models.repository import MongoRepository
from ..security.hashing import Hashing
class UserService():
    @staticmethod
    def check_error_answer(user: users.UserCreate, details: dict):
        if 'errmsg' in details:       
            field = list(details['keyPattern'].keys())[0]
            value = user.__getattribute__(field)
            raise HTTPException(
                status_code=status.HTTP_412_PRECONDITION_FAILED,
                detail={
                    "type": "duplicate_key_error",
                    "loc": [
                        "body",
                        field
                    ],
                    "msg": f"There is already an user with {field} = {value}",
                    "input": value,
                    "ctx": {
                        "error": {}
                    }
                }
            )

    @staticmethod
    async def get_user(username: str) -> users.UserInDB:
        repo = MongoRepository()
        user_dict = await repo.get_by_field(match=username, collection_type='users', field='user_name')
        result = users.UserInDB(**user_dict)
        return result
    
    @staticmethod
    async def create_user(user: users.UserCreate):
        repository = MongoRepository()
        user_in_db = user.to_userdb(hashed_password=Hashing.get_password_hash(user.password))
        answer = await repository.add(user_in_db)
        UserService.check_error_answer(user, answer)
        response_user = users.UserModel(**answer)
        return response_user