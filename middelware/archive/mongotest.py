from pymongo import MongoClient
from bson.json_util import dumps

class MongoAPI:
    def __init__(self, data):
        self.client = MongoClient("mongodb://192.168.178.100:27017/")  
      
        database = data['database']
        collection = data['collection']
        cursor = self.client[database]
        self.collection = cursor[collection]
        self.data = data
    
    def readReviews(self):
        documents = self.collection.find()
        return documents
    
    def writeReviews(self, data):
        new_document = data['Document']
        response = self.collection.insert_one(new_document)
        output = {'Status': 'Successfully Inserted',
                  'Document_ID': str(response.inserted_id)}
        return output
    
    def updateReviews(self, data):
        # return "updateReviews"
        filt = self.data['Filter']
        updated_data = {"$set": self.data['DataToBeUpdated']}
        response = self.collection.update_one(filt, updated_data)
        output = {'Status': 'Successfully Updated' if response.modified_count > 0 else "Nothing was updated."}
        return output
    
    def deleteReviews(self, data):
        filt = data['Document']
        response = self.collection.delete_one(filt)
        output = {'Status': 'Successfully Deleted' if response.deleted_count > 0 else "Document not found."}
        return output
    
    def readReviewsAsJSON(self):
        returnStr = "["
        documents = self.readReviews()
        for doc in documents:
            doc['_id'] = str(doc['_id'])
            newStr = dumps(doc, indent=4)
            returnStr+= newStr + ",\n"
            # print(newStr)
            # x = json.loads(newStr, object_hook=lambda d: SimpleNamespace(**d))
            # print(x._id + " " + x.name + " " + x.cuisine + " " + str(x.rating))
        return returnStr[:-1] + "]"