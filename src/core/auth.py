from datetime import datetime, timedelta

from core.config import Settings
from fastapi import Depends, HTTPException
import jwt
from passlib.context import CryptContext


class Auth():

    def __init__(self, settings: Settings) -> None:
        self.hasher = CryptContext(schemes=["bcrypt"])
        self.secret = settings.SECRET_KEY

    def encode_password(self, password):
        return self.hasher.hash(password)

    def verify_password(self, password, encoded_password):
        return self.hasher.verify(password, encoded_password)

    def encode_token(self, username: str, settings: Settings):
        payload = {
            "exp": datetime.utcnow() + timedelta(days=0, minutes=30),
            "iat": datetime.utcnow(),
            "scope": "access_token",
            "sub": username,
        }
        return jwt.encode(
            payload,
            self.secret,
            algorithm=settings.ALGORITHM,
        )

    def decode_token(self, token, settings: Settings):
        try:
            payload = jwt.decode(token, self.secret, algorithms=[settings.ALGORITHM])
            if payload["scope"] == "access_token":
                return payload["sub"]
            raise HTTPException(status_code=401, detail="Scope for the token is invalid")
        except jwt.ExpiredSignatureError:
            raise HTTPException(status_code=401, detail="Token expired")
        except jwt.InvalidTokenError:
            raise HTTPException(status_code=401, detail="Invalid token")

    def encode_refresh_token(self, username: str, settings: Settings = Depends()):
        payload = {
            "exp": datetime.utcnow() + timedelta(days=0, hours=10),
            "iat": datetime.utcnow(),
            "scope": "refresh_token",
            "sub": username,
        }
        return jwt.encode(
            payload,
            self.secret,
            algorithm=settings.ALGORITHM,
        )

    def refresh_token(self, refresh_token: str, settings: Settings):
        try:
            payload = jwt.decode(refresh_token, self.secret, algorithms=[settings.ALGORITHM])
            if (payload["scope"] == "refresh_token"):
                username = payload["sub"]
                new_token = self.encode_token(username)
                return new_token
            raise HTTPException(status_code=401, detail="Invalid scope for token")
        except jwt.ExpiredSignatureError:
            raise HTTPException(status_code=401, detail="Refresh token expired")
        except jwt.InvalidTokenError:
            raise HTTPException(status_code=401, detail="Invalid refresh token")
