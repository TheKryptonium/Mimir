from .models import User
from sqlmodel.ext.asyncio import AsyncSession
from sqlmodel import select
from .schemas import UserCreateModel
from .utils import generate_password, verify_password

class UserService:
    async def get_user_by_email(self, session: AsyncSession, email):
        statement = select(User).where(User.email==email)
        result  =  await session.execute(statement)
        return  result.scalars().first()
    
    async def user_exists(self, session: AsyncSession, email):
        user = await self.get_user(session, email)
        return True if user is not None else False
    
    async def create_user(self, session: AsyncSession, user_data: UserCreateModel):
        user_data_dict = user_data.model_dump()
        new_user = User(**user_data_dict)
        new_user.password_hash = generate_password(user_data_dict['password'])
        session.add(new_user)
        await session.commit()
        return new_user
        