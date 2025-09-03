from pymongo import MongoClient

uri = (
    "mongodb://cats_test:Ic2lQsPMJH5BG0gq@"
    "ac-sukun0c-shard-00-00.6oopp7o.mongodb.net:27017,"
    "ac-sukun0c-shard-00-01.6oopp7o.mongodb.net:27017,"
    "ac-sukun0c-shard-00-02.6oopp7o.mongodb.net:27017/"
    "?replicaSet=atlas-sukun0c-shard-0&tls=true&authSource=admin&retryWrites=true&w=majority"
)

client = MongoClient(uri, serverSelectionTimeoutMS=20000)
print(client.admin.command("ping"))  # очікуємо {'ok': 1.0}
