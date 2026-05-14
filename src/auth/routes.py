from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from .schemas import UserCreateModel, UserModel, UserLoginModel
from .service import UserService
from src.db.main import get_session
from sqlalchemy.ext.asyncio.session import AsyncSession
from .utils import create_token_access, decode_token, verify_password
from datetime import timedelta

auth_router = APIRouter()
user_service = UserService()

REFRESH_TOKEN_EXPIRY = timedelta(days=7)

@auth_router.post('/signup', response_model=UserModel, status_code=status.HTTP_201_CREATED)
async def create_user(user_data: UserCreateModel, session: AsyncSession = Depends(get_session)):
    email = user_data.email
    user_exists = await user_service.user_exists(session, email)
    
    if user_exists:
        raise HTTPException(status.HTTP_403_FORBIDDEN, detail=f"user with {email} already exists")
    else:
        new_user = await user_service.create_user(session, user_data)
    
    return new_user


@auth_router.post("/login", status_code=status.HTTP_200_OK)
async def login_user(login_data: UserLoginModel, session: AsyncSession = Depends(get_session)):
    email = login_data.email
    password = login_data.password
    
    user = await user_service.get_user_by_email(session, email)
    
    if user is not None:
        password_valid = verify_password(password, user.password_hash)
        
        if password_valid:
            access_token = create_token_access(
                {
                    'email': user.email,
                    'uid': str(user.uid),
                    
                }
            )
            
            refresh = create_token_access(
                {
                    'email': user.email,
                    'uid': str(user.uid)                    
                },
                refresh = True,
                expiry = REFRESH_TOKEN_EXPIRY
            )
            
            return JSONResponse(
                content={
                    "message": "Login succesful",
                    "access_token": access_token,
                    "refresh_token": refresh,
                    "user":{
                        "email": user.email,
                        "uid": str(user.uid)
                    }
                }
                
            )
            
    
    raise HTTPException(status.HTTP_403_FORBIDDEN, detail=f'Invalid Email or password') 
