
from ..models import users
from ..models.repository import MongoRepository
from ..security.hashing import Hashing

class UserService():
    @staticmethod
    async def get_user(username: str) -> users.UserInDB:
        repo = MongoRepository()
        user_dict = await repo.get_by_field(match=username, collection_type='users', field='username')
        result = users.UserInDB(**user_dict)
        return result
    
    @staticmethod
    async def create_user(user: users.UserCreate):
        repository = MongoRepository()
        user_in_db = user.to_userdb(hashed_password=Hashing.get_password_hash(user.password))
        created_user = await repository.add(user_in_db)
        response_user = users.UserModel(**created_user)
        return response_user