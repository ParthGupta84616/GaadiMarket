import json
from pymongo import MongoClient
from bson import ObjectId

# Connect to MongoDB
client = MongoClient('localhost', 27017)
db = client['PartsOnline']
collection = db['locations']

# Read the JSON file
with open('location.json', 'r') as file:
    data = json.load(file)

# Convert $oid to ObjectId
for item in data:
    if '_id' in item and '$oid' in item['_id']:
        item['_id'] = ObjectId(item['_id']['$oid'])

# Insert the data into the collection
collection.insert_many(data)

print("Data inserted successfully")