import datetime
from bson import ObjectId
from pydantic import BaseModel, Field
import uuid

class BaseComment(BaseModel):
    text: str

class Comment(BaseComment):
    id: str = Field(default_factory=uuid.uuid4, alias="_id")
    created_at: datetime.datetime
    updated_at: datetime.datetime
    user_id: str
    profile_image: str
    post_id: str
    username: str


class CommentIn(BaseComment):
    pass