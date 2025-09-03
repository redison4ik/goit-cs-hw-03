import os
from pymongo import MongoClient

uri = os.getenv("MONGODB_URI")
client = MongoClient(uri)
print(client.list_database_names())
