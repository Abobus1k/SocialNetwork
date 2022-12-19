from pydantic import BaseSettings
from starlette.config import Config

config = Config(".env")


class Settings(BaseSettings):
    ACCESS_TOKEN_EXPIRE_MINUTES = 120
    ALGORITHM = "HS256"
    ATLAS_URI: str
    DB_NAME: str
    SECRET_KEY: str
    DEFAULT_PROFILE_IMAGE: str

    class Config:
        env_file = ".env"
