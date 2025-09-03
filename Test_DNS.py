from pymongo import MongoClient
uri = "mongodb://cats_test:Ic2lQsPMJH5BG0gq@host1:27017,host2:27017,host3:27017/\
?replicaSet=atlas-XXXXX-shard-0&tls=true&authSource=admin&retryWrites=true&w=majority"
client = MongoClient(uri, serverSelectionTimeoutMS=20000)
print(client.admin.command("ping"))