from pymongo import MongoClient
from bson.objectid import ObjectId
import os

MONGO_DB = os.environ.get('MONGOBD_HOST', "localhost")
client = MongoClient('mongodb://'+MONGO_DB+':27017/')
db = client.contact_book
contact_db = db.contact
counter_db = db.counter
note_db=db.note