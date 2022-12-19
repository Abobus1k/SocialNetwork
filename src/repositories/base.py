from dotenv import dotenv_values
from pymongo import MongoClient

config = dotenv_values(".env")

class BaseRepository:
    def __init__(self):
        client = MongoClient(config["ATLAS_URI"])
        self.database = client[config["DB_NAME"]]