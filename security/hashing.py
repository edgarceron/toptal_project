
from passlib.context import CryptContext

class Hashing:
    PWD_CONTEXT = CryptContext(schemes=["bcrypt"], deprecated="auto")

    @staticmethod
    def verify_password(plain_password, hashed_password):
        return Hashing.PWD_CONTEXT.verify(plain_password, hashed_password)

    @staticmethod
    def get_password_hash(password):
        return Hashing.PWD_CONTEXT.hash(password)