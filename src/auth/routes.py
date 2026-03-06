from fastapi import APIRouter, Depends, HTTPException, status
from .schemas import UserCreateModel, UserModel
from .service import UserService
from src.db.main import get_session
from sqlmodel.ext.asyncio.session import AsyncSession

auth_router = APIRouter()
user_service = UserService()

@auth_router.post('/signup', response_model=UserModel, status_code=status.HTTP_201_CREATED)
async def create_user(user_data: UserCreateModel, session: AsyncSession = Depends(get_session)):
    email = user_data.email
    user_exists = await user_service.user_exists(session, email)
    
    if user_exists:
        raise HTTPException(status.HTTP_403_FORBIDDEN, detail=f"user with {email} already exists")
    else:
        new_user = await user_service.create_user(session, user_data)