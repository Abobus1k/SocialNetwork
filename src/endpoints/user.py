from fastapi import APIRouter, Body, status, File, Response, Security, Depends
from typing import List
from repositories.user import UserRepository
from models.user import User, UserIn
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from models.post import Post
# from pymongo import ReturnDocument
# from fastapi.responses import JSONResponse, FileResponse

router = APIRouter()

users = UserRepository()
security = HTTPBearer()

@router.get("/", response_description="List all users", response_model=List[User])
def list_users(limit : int = 100, skip : int = 0, _credentials: HTTPAuthorizationCredentials = Security(security)):
    return users.get_all(limit=limit, skip=skip)

@router.put("/update", response_description="Update user profile", response_model=User)
def update(credentials: HTTPAuthorizationCredentials = Security(security), u : UserIn = Body(...)):
    user = users.get_current_user(credentials.credentials)
    return users.update(user["_id"], u)

@router.put("/profile_image", response_description="Set a new profile image")
def upload_file(credentials: HTTPAuthorizationCredentials = Security(security), file: bytes = File()):
    file_id = users.get_file_id(file)
    user = users.get_current_user(credentials.credentials)
    return users.update_profile_image(user["_id"], file_id)

@router.post("/upload_default", response_description="Upload default image", status_code=status.HTTP_201_CREATED)
def upload_default_img(file : bytes = File()):
   users.upload_image(file)

@router.put("/name_surname", response_description="Update name and surname", response_model=User)
def update_name_and_surname(name : str, surname : str, credentials: HTTPAuthorizationCredentials = Security(security)):
    user = users.get_current_user(credentials.credentials)
    return users.update_name_surname(user["_id"], name, surname)

@router.put("/username", response_description="Update username", response_model=User)
def update_user_username(username : str, credentials: HTTPAuthorizationCredentials = Security(security)):
    user = users.get_current_user(credentials.credentials)
    return users.update_username(user["_id"], username)

@router.delete("/", response_description="Delete account")
def delete_user(credentials: HTTPAuthorizationCredentials = Security(security)):
    user = users.get_current_user(credentials.credentials)
    users.delete(user["_id"])

@router.get("/get_image", response_description="Get profile image")
def get_profile_image(credentials: HTTPAuthorizationCredentials = Security(security)):
    user = users.get_current_user(credentials.credentials)
    return Response(users.get_file(user["_id"]))

@router.put("/bio", response_description="Update bio", response_model=User)
def update_bio(bio : str, credentials: HTTPAuthorizationCredentials = Security(security)):
    user = users.get_current_user(credentials.credentials)
    return users.update_bio(user["_id"], bio)

@router.put("/subscribe", response_description="Subscibe on user")
def subscribe_user(sub_id : str, credentials: HTTPAuthorizationCredentials = Security(security)):
    user = users.get_current_user(credentials.credentials)
    return users.subscribe(user["_id"], sub_id)

@router.put("/unsubscribe", response_description="Unsubscribe user")
def unsubscribe_user(sub_id : str, credentials: HTTPAuthorizationCredentials = Security(security)):
    user = users.get_current_user(credentials.credentials)
    return users.unsubsribe(user["_id"], sub_id)

@router.get("/get_subscribers", response_description="List subscribers", response_model=List[User])
def get_subscribers(credentials: HTTPAuthorizationCredentials = Security(security)):
    user = users.get_current_user(credentials.credentials)
    return users.get_subscribers(user["_id"])

@router.get("/get_subscriptions", response_description="List subscriptions", response_model=List[User])
def get_subscriptions(credentials: HTTPAuthorizationCredentials = Security(security)):
    user = users.get_current_user(credentials.credentials)
    return users.get_subscriptions(user["_id"])

@router.put("/like", response_description="Like post", response_model=Post)
def like(post_id : str, credentials: HTTPAuthorizationCredentials = Security(security)):
    user = users.get_current_user(credentials.credentials)
    return users.set_like(post_id, user["_id"])

@router.put("/dislike", response_description="Dislike post", response_model=Post)
def dislike(post_id : str, credentials: HTTPAuthorizationCredentials = Security(security)):
    user = users.get_current_user(credentials.credentials)
    return users.unset_like(post_id, user["_id"])
