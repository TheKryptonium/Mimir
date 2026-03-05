from sqlmodel import SQLModel, Field, Column
import sqlalchemy.dialects.postgresql as pg
from datetime import datetime
import uuid

class Book(SQLModel, table=True):
    __tablename__ = "books"
    
    id: uuid.UUID  = Field(
        default_factory = uuid.uuid4,
        sa_column = Column(
            pg.UUID,
            nullable = False,
            primary_key = True,
        )
    )
    title: str
    author: str
    year: int
    created_at: datetime = Field(sa_column = Column(pg.TIMESTAMP(timezone=True), default=datetime.now))
    updated_at: datetime = Field(sa_column = Column(pg.TIMESTAMP(timezone=True), default=datetime.now))
    
    
    def __repr__(self):
        return f'<Book {self.title}>'