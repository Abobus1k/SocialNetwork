import datetime
from datetime import date
from typing import Optional
import uuid

import pydantic
from pydantic import BaseModel, constr, EmailStr, Field

# from bson.objectid import ObjectId


class User(BaseModel):
    """The user class represents how the user is stored in the database

    Args:
        BaseModel ([type]): Pydantic basemodel
    """
    _id: str = Field(default_factory=uuid.uuid4, alias="_id")
    profile_image: str = ""
    name: str = ""
    surname: str = ""
    bio: str = ""
    email: Optional[pydantic.EmailStr]
    hashed_password: str
    username: str
    gender: str = ""
    age: Optional[date]
    liked_posts: list = []
    subscriptions: list = []
    subscribers: list = []
    created_at: datetime.datetime
    updated_at: datetime.datetime


class UserIn(BaseModel):
    """The userin class represents what information the user can input after regestration

    Args:
        BaseModel (_type_): pydantic basemodel
    """
    name: str
    surname: str
    bio: str
    email: EmailStr
    gender: str
    age: date


class AuthModel(BaseModel):
    """The userin class represents what information the user input when regestration

    Args:
        BaseModel (_type_): pydantic basemodel
    """
    username: str
    password: constr(min_length=8)
