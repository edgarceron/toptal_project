# Script to create index in MongoBD
from pymongo import MongoClient, errors
MONGODB_URL = "mongodb://root:example@127.0.0.1:27017"
client = MongoClient(MONGODB_URL)
db = client['renting']
collection = db['apartments']

try:
    index_name = collection.create_index([("location", "2dsphere")])
    print(f"2dsphere index created or already exists: {index_name}")
except errors.PyMongoError as e:

    print(f"An error occurred: {e}")