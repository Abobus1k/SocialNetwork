import datetime
from typing import List, Optional

from bson import ObjectId
from core.auth import Auth
from core.config import Settings
from database.db import Database
from fastapi import HTTPException, status
from fastapi.encoders import jsonable_encoder
from fastapi.security import HTTPBearer
import gridfs
from models.post import Post
from models.user import User, UserIn

security = HTTPBearer()


class UserRepository(Database):

    """
    UserRepository is a helper class for user endpoints

    Inheritance:
        Database:
            Attributes:
                database : provides MongoDB Connection
    """

    # User's profile methods

    def get_all(self, limit: int = 100, skip: int = 0) -> List[User]:
        """Return list of users in database

        Args:
            limit (int, optional): number of users. Defaults to 100.
            skip (int, optional): skip some users. Defaults to 0.

        Returns:
            List[User]: all users in db
        """
        query = self.database["users"].find(limit=limit)
        return list(query)

    def get_by_id(self, _id: int) -> Optional[User]:
        """Get the user by id

        Args:
            _id (int): user id

        Raises:
            HTTPException: 404_NOT_FOUND Error

        Returns:
            Optional[User]: if user was found in db
        """
        if (user := self.database["users"].find_one({"_id": _id})) is not None:
            return user
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"User with ID {_id} not found")

    def create(self, _user: dict) -> User:
        """Creates a user during registration

        Args:
            _user (dict): contains username and password

        Returns:
            User: created user
        """
        settings = Settings()
        user = User(
            username=_user["username"],
            hashed_password=_user["hashed_password"],
            created_at=datetime.datetime.utcnow(),
            updated_at=datetime.datetime.utcnow(),
        )
        user.profile_image = settings.DEFAULT_PROFILE_IMAGE
        user = jsonable_encoder(user)
        new_user = self.database["users"].insert_one(user)
        created_user = self.database["users"].find_one(
            {"_id": new_user.inserted_id},
        )
        return created_user

    def update(self, user_id: str, _user: UserIn) -> User:
        """Update name, surname, bio, age, gender, email at the user

        Args:
            user_id (str): user id
            _user (UserIn): contains new name, surname, bio, age, gender, email

        Returns:
            User: updated user
        """
        self.database["users"].find_one_and_update({"_id": user_id},
                                                   {"$set": {
                                                        "name": _user.name,
                                                        "surname": _user.surname,
                                                        "bio": _user.bio,
                                                        "age": str(_user.age),
                                                        "gender": _user.gender,
                                                        "email": _user.email,
                                                    }},
                                                   )
        updated_user = self.database["users"].find_one({"_id": user_id})
        return updated_user

    def upload_image(self, image: bytes):
        """Upload default image to database

        Args:
            image (bytes): bytes of the image
        """
        imgs_profile = gridfs.GridFS(self.database, "imgs_profile")
        imgs_profile.put(image)

    def get_by_email(self, email: str) -> User:
        """Get user by email

        Args:
            email (str): user email

        Raises:
            HTTPException: 404_NOT_FOUND Error

        Returns:
            User: found user
        """
        if (user := self.database["users"].find_one({"email": email})) is not None:
            return user
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"User with email: {email} not found")

    def get_file_id(self, image: bytes) -> str:
        """Get id of the image

        Args:
            image (bytes): bytes of the image

        Returns:
            str: id
        """
        imgs_profile = gridfs.GridFS(self.database, "imgs_profile")
        obj = imgs_profile.put(image)
        return str(imgs_profile.get(obj)._id)

    def update_name_surname(self, user_id: str, new_name: str, new_surname: str) -> User:
        """Update name and surname of the user

        Args:
            user_id (str): user id
            new_name (str): new name of the user
            new_surname (str): new surname of the user

        Returns:
            User: updated user
        """
        self.database["users"].find_one_and_update({"_id": user_id},
                                                   {"$set": {
                                                        "name": new_name,
                                                        "surname": new_surname,
                                                    }},
                                                   )
        updated_user = self.database["users"].find_one({"_id": user_id})
        return updated_user

    def update_profile_image(self, user_id: str, file_id: str) -> User:
        """Update profile image of the user (update profile id field in user model)

        Args:
            user_id (str): user id
            file_id (str): new profile image id

        Returns:
            User: updated user
        """

        settings = Settings()
        user = self.database["users"].find_one({"_id": user_id})

        if user["profile_image"] != settings.DEFAULT_PROFILE_IMAGE:
            imgs_profile = gridfs.GridFS(self.database, "imgs_profile")
            imgs_profile.delete(ObjectId(user["profile_image"]))

        self.database["users"].find_one_and_update({"_id": user_id},
                                                   {"$set": {"profile_image": file_id}},
                                                   )
        updated_user = self.database["users"].find_one({"_id": user_id})
        return updated_user

    def update_username(self, user_id: str, new_username: str) -> User:
        """Update username of the user

        Args:
            user_id (str): user id
            new_username (str): new user username

        Returns:
            User: updated user
        """
        self.database["users"].find_one_and_update({"_id": user_id},
                                                   {"$set": {"username": new_username}},
                                                   )
        updated_user = self.database["users"].find_one({"_id": user_id})
        return updated_user

    def delete(self, user_id: str):
        """Delete user

        Args:
            user_id (str): user id
        """
        self.database["users"].find_one_and_delete({"_id": user_id})

    def get_file(self, user_id: str) -> bytes:
        """Get bytes of user's profile image

        Args:
            user_id (str): user id

        Returns:
            bytes: bytes of file
        """
        user = self.database["users"].find_one({"_id": user_id})
        imgs_profile = gridfs.GridFS(self.database, "imgs_profile")
        image = imgs_profile.get(ObjectId(user["profile_image"]))
        return image.read()

    def update_bio(self, user_id: str, new_bio: str) -> User:
        """Update user bio

        Args:
            user_id (str): user id
            new_bio (str): new bio of the user

        Returns:
            User: _description_
        """
        self.database["users"].find_one_and_update({"_id": user_id},
                                                   {"$set": {"bio": new_bio}},
                                                   )
        updated_user = self.database["users"].find_one({"_id": user_id})
        return updated_user

    def subscribe(self, user_id: str, sub_user_id: str):
        """Subscribe on the user

        Args:
            user_id (str): user id
            sub_user_id (str): subscription's id
        """
        self.database["users"].find_one_and_update({"_id": user_id},
                                                   {"$push": {"subscriptions": sub_user_id}},
                                                   )
        self.database["users"].find_one_and_update({"_id": sub_user_id},
                                                   {"$push": {"subscribers": user_id}},
                                                   )

    def unsubsribe(self, user_id: str, sub_user_id: str):
        """Unsubscribe on the user

        Args:
            user_id (str): user id
            sub_user_id (str): subscription's id
        """
        self.database["users"].find_one_and_update({"_id": user_id},
                                                   {"$pull": {"subscriptions": sub_user_id}},
                                                   )
        self.database["users"].find_one_and_update({"_id": sub_user_id},
                                                   {"$pull": {"subscribers": user_id}},
                                                   )

    def __get_sub_helper__(self, user_id: str, what_need: str) -> List[User]:
        """Helper for get subscribers and subscriptions.
        That functions appeared because the implementations of getting subscribers and subscriptions
        are very similar

        Args:
            user_id (str): user id
            what_need (str): subscription or subscriber

        Returns:
            List[User]: List of subscriptions or subscribers
        """
        user = self.database["users"].find_one({"_id": user_id})
        res = []
        for u_id in user[what_need]:
            _user = self.database["users"].find_one({"_id": u_id})
            res.append(_user)
        return res

    def get_subscribers(self, user_id: str) -> List[User]:
        """Get list of subscribers

        Args:
            user_id (str): user id

        Returns:
            List[User]: subscribers
        """
        return self.__get_sub_helper__(user_id, "subscribers")

    def get_subscriptions(self, user_id: str) -> List[User]:
        """Get list of subscriptions

        Args:
            user_id (str): user id

        Returns:
            List[User]: subscriptions
        """
        return self.__get_sub_helper__(user_id, "subscriptions")

    def check_username(self, username: str) -> bool:
        """Verify username

        Args:
            username (str): username

        Returns:
            bool: if the user is in the database or not
        """
        if self.database["users"].find_one({"username": username}) is None:
            return False
        return True

    def get_by_username(self, username: str) -> Optional[User]:
        """Get user by username

        Args:
            username (str): username

        Returns:
            Optional[User]: if the user in database
        """
        return self.database["users"].find_one({"username": username})

    # User' login methods

    def signup(self, username: str, password: str) -> User:
        """Signup user

        Args:
            username (str): username
            password (str): password

        Returns:
            User: created user
        """
        settings = Settings()
        auth_handler = Auth(settings)
        if self.check_username(username):
            return HTTPException(status_code=401, detail="Account already exists")
        try:
            hashed_password = auth_handler.encode_password(password)
            user = {"username": username, "hashed_password": hashed_password}
            return self.create(user)
        except: # noqa FIXME
            return HTTPException(status_code=401, detail="Failed to signup user")

    def login(self, username: str, password: str) -> User:
        """Login user

        Args:
            username (str): username
            password (str): password

        Raises:
            HTTPException: 401 Error (invalid username or password)

        Returns:
            User: if user signed up
        """
        settings = Settings()
        auth_handler = Auth(settings)
        user = self.get_by_username(username)
        if self.check_username(username) is False:
            return HTTPException(status_code=401, detail="Invalid username")
        if (not auth_handler.verify_password(password, user["hashed_password"])):
            return HTTPException(status_code=401, detail="Invalid password")
        return user

    def get_current_user(self, token: str) -> User:
        """Get logined user

        Args:
            token (str): user token

        Returns:
            User: if user logined
        """
        settings = Settings()
        auth_handler = Auth(settings)
        username = auth_handler.decode_token(token, settings)
        return self.get_by_username(username)

    # User's post methods

    def set_like(self, post_id: str, user_id: str) -> Post:
        """Set like on the post

        Args:
            post_id (str): post id
            user_id (str): user id

        Returns:
            Post: updated post
        """
        self.database["users"].find_one_and_update({"_id": user_id},
                                                   {"$push": {"liked_posts": post_id}},
                                                   )
        self.database["posts"].find_one_and_update({"_id": post_id},
                                                   {"$inc": {"likes": 1}},
                                                   )
        updated_post = self.database["posts"].find_one({"_id": post_id})
        return updated_post

    def unset_like(self, post_id: str, user_id: str) -> Post:
        """Unset like from the post

        Args:
            post_id (str): post id
            user_id (str): user id

        Returns:
            Post: updated post
        """
        self.database["users"].find_one_and_update({"_id": user_id},
                                                   {"$pull": {"liked_posts": post_id}},
                                                   )
        self.database["posts"].find_one_and_update({"_id": post_id},
                                                   {"$inc": {"likes": -1}},
                                                   )
        created_post = self.database["posts"].find_one({"_id": post_id})
        return created_post

    def get_profile_image_id(self, user_id: str) -> str:
        """Get profile image id from the user

        Args:
            user_id (str): user id

        Returns:
            str: profile image id
        """
        profile_image_id = self.database["users"].find_one({"_id": user_id})
        return profile_image_id
