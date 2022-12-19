from datetime import date, datetime
import datetime
from typing import Optional
import pydantic
from pydantic import BaseModel, EmailStr, validator, constr, Field
from typing import Optional
import uuid
import pydantic
# from bson.objectid import ObjectId

class User(BaseModel):
    id: str = Field(default_factory=uuid.uuid4, alias="_id")
    profile_image: str = ""
    name: str = ""
    surname : str = ""
    bio : str = ""
    email: Optional[pydantic.EmailStr]
    hashed_password: str
    username: str
    gender: str = ""
    age: Optional[date]
    liked_posts : list = []
    subscriptions : list = []
    subscribers : list = []
    created_at: datetime.datetime
    updated_at: datetime.datetime

class UserIn(BaseModel):
    name: str
    surname : str
    bio : str
    email: EmailStr
    gender : str
    age : date

class AuthModel(BaseModel):
    username : str
    password : constr(min_length=8)