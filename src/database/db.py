from core.config import Settings
from pymongo import MongoClient


class Database():
    def __init__(self) -> None:
        settings = Settings()
        client = MongoClient(settings.ATLAS_URI)
        self.database = client[settings.DB_NAME]
