import datetime
from bson import ObjectId
from pydantic import BaseModel, Field
import uuid


class BasePost(BaseModel):
    description: str
    tags: list

class Post(BasePost):
    id: str = Field(default_factory=uuid.uuid4, alias="_id")
    created_at: datetime.datetime
    updated_at: datetime.datetime
    user_id: str
    username: str
    profile_image: str
    image: str
    likes: int
    comments=list

class PostIn(BasePost):
    pass