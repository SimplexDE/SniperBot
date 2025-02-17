from typing import List

from pymongo import MongoClient


class MongoDB:
    def __init__(self, database: str):
        self.client: MongoClient = MongoClient("mongodb://192.168.2.10:27017")
        self.database = self.client[database]

    def connection(self):
        return self.client

    def count(self, collection_name: str):
        collection = self.collection(collection_name)
        return collection.estimated_document_count()

    def collection(self, name: str):
        return self.database[name]

    def insert(
        self, collection_name: str, document: dict = None, documents: List[dict] = None
    ):
        collection = self.collection(collection_name)

        if document is not None:
            collection.insert_one(document)
        if documents is not None:
            collection.insert_many(documents)

    def update(self, collection_name: str, _filter: dict, new: dict):
        collection = self.collection(collection_name)
        collection.update_one(_filter, {"$set": new})

    def query(self, collection_name: str, index: dict = None):
        collection = self.collection(collection_name)

        if index is not None:
            return collection.find(index)
        return collection.find()

    def query_one(self, collection_name: str, index: dict = None):
        collection = self.collection(collection_name)

        if index is not None:
            return collection.find_one(index)
        return collection.find_one()

    def delete_one(self, collection_name: str, index: dict):
        collection = self.collection(collection_name)

        return collection.delete_one(index)
