from pydantic import BaseModel
from uuid import UUID
from datetime import datetime

class Book(BaseModel):
    id: UUID
    title: str
    author: str
    year: int
    created_at: datetime
    updated_at: datetime
    
class BookCreateModel(BaseModel):
    title: str
    author: str
    year: int
    
    
class BookUpdateModel(BaseModel):
    title: str
    author: str
    year: int