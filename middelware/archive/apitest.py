from flask import Flask, request, json, Response
from pymongo import MongoClient

from mongotest import MongoAPI

if __name__ == '__main__':
    data = {
        "database": "business",
        "collection": "reviews",
    }
    mongo_obj = MongoAPI(data)
    print(mongo_obj.readReviewsAsJSON())