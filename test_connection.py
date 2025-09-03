import os
from pymongo import MongoClient
uri = os.getenv("MONGODB_URI")
client = MongoClient(uri, serverSelectionTimeoutMS=5000)  # 5 c
try:
    print(client.admin.command("ping"))  # {'ok': 1.0}
except Exception as e:
    print("CONNECTION ERROR:", e)
