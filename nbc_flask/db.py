from pymongo import MongoClient


def get_db():
    client = MongoClient("mongodb+srv://test:<password>@cluster0.kgq1f.mongodb.net/myFirstDatabase?retryWrites=true&w=majority")

    return client

