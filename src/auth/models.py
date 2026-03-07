from sqlmodel import SQLModel, Field, Column
import sqlalchemy.dialects.postgresql as pg
from datetime import datetime
import uuid

class User(SQLModel, table= True):
    __tablename__="users"
    
    uid: uuid.UUID = Field(
        default_factory = uuid.uuid4,
        sa_column = Column(
            pg.UUID,
            nullable = False,
            primary_key = True,
        )
    )
    username: str
    email: str
    firstname: str
    lastname: str
    is_verified: bool = False
    password_hash: str = Field(exclude = True)
    created_at: datetime = Field(sa_column = Column(pg.TIMESTAMP(timezone=True), default=datetime.now))
    updated_at: datetime = Field(sa_column = Column(pg.TIMESTAMP(timezone=True), default=datetime.now))
    
    def __repr__(self):
        return f'<User {self.username}>'