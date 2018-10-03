# sendToDb.py
from pymongo import MongoClient

msg = {"roverMsg": "tagged", "code": 'T'}

client = MongoClient('mongodb://localhost:27017/')
db = client.roverMessages
db.roverMessages.insert(msg)

print('Message Inserted')
