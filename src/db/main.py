from sqlmodel import create_engine, text, SQLModel
from sqlalchemy.ext.asyncio import AsyncEngine
from src.config import Config
from sqlalchemy.ext.asyncio.session import AsyncSession
from sqlalchemy.orm import sessionmaker

# 1. Create the db engine, asynchronous when we deal with an asynchronous dbms like postgresql and synchronous when we deal with a syncrhonous dbms like sqlite
engine = AsyncEngine( 
    create_engine(
        url = Config.DATABASE_URL,
        echo = True
    )
)

#2. Initialize the database
async def init_db()->None: 
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all) #Create all tables in the database based on the models defined in SQLModel
        
#3. Get/Instantiate a session
async def get_session()->AsyncSession:
    Session = sessionmaker(
        bind = engine,
        class_ = AsyncSession,
        expire_on_commit = False
    )  
    
    async with Session() as session:
        yield session 