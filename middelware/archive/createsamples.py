from pymongo import MongoClient
from random import randint
import json
from types import SimpleNamespace
from bson.json_util import dumps, loads

from business import Business


#Step 1: Connect to MongoDB - Note: Change connection string as needed
client = MongoClient("192.168.178.100:27017")
db=client.business
#fivestar = db.reviews.find_one({'rating': 5})
#print(fivestar)
for doc in db.reviews.find({'rating': 5}):
    #print(dumps(str(doc).replace("ObjectId(","").replace(")",""), indent=2))
    doc['_id'] = str(doc['_id'])
    newStr = dumps(doc)
    print(newStr)
    x = json.loads(newStr, object_hook=lambda d: SimpleNamespace(**d))
    print(x._id + " " + x.name + " " + x.cuisine + " " + str(x.rating))
# stargroup=db.reviews.aggregate(
# # The Aggregation Pipeline is defined as an array of different operations
# [
# # The first stage in this pipe is to group data
# { '$group':
#     { '_id': "$rating",
#      "count" : 
#                  { '$sum' :1 }
#     }
# },
# # The second stage in this pipe is to sort the data
# {"$sort":  { "_id":1}
# }
# # Close the array with the ] tag             
# ] )
# # Print the result
# for group in stargroup:
#     print(group)

busi=Business("asdf", "name2", 2, "cuisine2")
print(busi.toString())