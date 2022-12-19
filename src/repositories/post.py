from typing import List, Optional
import datetime as dt
from datetime import datetime
from models.post import Post, PostIn
from models.comment import Comment, CommentIn
from .base import BaseRepository
from fastapi.encoders import jsonable_encoder
from fastapi import HTTPException, status
import gridfs
from bson import ObjectId
from .user import UserRepository

users = UserRepository()

class PostRepository(BaseRepository):

    def create(self, user_id:str, file_id:str, p: PostIn) ->Post:
        post = Post(
            description=p.description,
            tags=p.tags,
            image=file_id,
            user_id=user_id,
            username=self.get_username(user_id),
            profile_image=self.get_profile_image_id(user_id),
            likes=0,
            created_at=dt.datetime.utcnow(),
            updated_at=dt.datetime.utcnow(),
            comments=[]
        )
        post = jsonable_encoder(post)
        new_post = self.database["posts"].insert_one(post)
        created_post = self.database["posts"].find_one(
            {"_id": new_post.inserted_id}
        )
        return created_post

    def get_all(self, limit: int = 100, skip: int = 0) -> List[Post]:
        query = self.database["posts"].find(limit=limit)
        return list(query)

    def sort_by_time(self,query:list):
        query=sorted(
            query,
            key=lambda x: datetime.strptime(x['updated_at'], "%Y-%m-%dT%H:%M:%S.%f"), reverse=True
        )
        sort_query=query
        return sort_query

    def get_feed(self, user_id:str)-> List[Post]:
        feed=[]
        user=self.database["users"].find_one({"_id":user_id})
        subs=user["subscriptions"]
        for sub_user in subs:
            query = self.get_all_by_id(sub_user)
            feed=feed+query
        sort_feed=self.sort_by_time(feed)
        return sort_feed

    def get_profile_feed(self, user_id: str)-> List[Post]:
        profile_feed=self.get_all_by_id(user_id)
        sort_profile_feed=self.sort_by_time(profile_feed)
        return sort_profile_feed

    def get_all_by_id(self,user_id:str) -> List[Post]:
        query = self.database["posts"].find({"user_id": user_id})
        found_posts=list(query)
        return found_posts

    def get_by_id(self, id : int) -> Optional[Post]:
        if (post := self.database["posts"].find_one({"_id": id})) is not None:
            found_post=post
            return found_post
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Post with ID {id} not found")

    def delete(self, id: str,user_id:str):
        x=self.database["posts"].find_one({"_id": id})
        if x["user_id"]!=user_id:
            raise  HTTPException(status_code=403, detail='No access to delete this post')
        else:
            self.database["posts"].find_one_and_delete({"_id": id})

    def get_file_id(self, file:bytes) ->str:
        imgs_post = gridfs.GridFS(self.database, "imgs_post")
        obj = imgs_post.put(file)
        post_id=str(imgs_post.get(obj)._id)
        return post_id

    def get_file(self, post_id : str) ->bytes:
        post = self.database["posts"].find_one({"_id" : post_id})
        imgs_post=gridfs.GridFS(self.database, "imgs_post")
        file = imgs_post.get(ObjectId(post["image"]))
        return file.read()

    def get_profile_image_id(self,user_id: str):
        profile_image_id=self.database["users"].find_one({"_id" : user_id})["profile_image"]
        return profile_image_id

    def get_username(self,user_id:str):
        username=self.database["users"].find_one({"_id" : user_id})["username"]
        return username

    def post_comment(self,post_id:str, user_id:str,c:CommentIn)->Comment:
        comment=Comment(
            text=c.text,
            created_at=dt.datetime.utcnow(),
            updated_at=dt.datetime.utcnow(),
            user_id=user_id,
            username=self.get_username(user_id),
            profile_image=self.get_profile_image_id(user_id),
            post_id=post_id
        )
        comment=jsonable_encoder(comment)
        new_comment=self.database["comments"].insert_one(comment)
        created_comment=self.database["comments"].find_one({"_id":new_comment.inserted_id})
        return created_comment

    def show_comments(self,post_id: str)->List[Comment]:
        comments=self.get_all_coms_by_id(post_id)
        sort_comments=self.sort_by_time(comments)
        return sort_comments

    def get_all_coms_by_id(self,post_id:str) -> List[Post]:
        query = self.database["comments"].find({"post_id": post_id})
        found_coms=list(query)
        return found_coms
