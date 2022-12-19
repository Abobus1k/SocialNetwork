from fastapi import Depends, APIRouter, Security
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from core.auth import Auth
from core.config import Settings
from models.user import AuthModel, User
from repositories.user import UserRepository

router = APIRouter()

security = HTTPBearer()
settings = Settings()
auth_handler = Auth(settings)

users = UserRepository()

@router.post('/signup', response_model=User)
def signup(user_details: AuthModel = Depends()):
    return users.signup(user_details.username, user_details.password)

@router.post('/login')
def login(user_details: AuthModel = Depends()):
    user = users.login(user_details.username, user_details.password)
    access_token = auth_handler.encode_token(user['username'], settings)
    refresh_token = auth_handler.encode_refresh_token(user['username'], settings)
    return {'access_token': access_token, 'refresh_token': refresh_token}

@router.get('/refresh_token')
def refresh_token(credentials: HTTPAuthorizationCredentials = Security(security)):
    refresh_token = credentials.credentials
    new_token = auth_handler.refresh_token(refresh_token, settings)
    return {'access_token': new_token}

@router.get("/user", response_model=User)
def get_current_user(credentials: HTTPAuthorizationCredentials = Security(security)):
    return users.get_current_user(credentials.credentials)