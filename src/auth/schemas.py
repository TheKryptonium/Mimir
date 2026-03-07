from pydantic import BaseModel, Field
import uuid
from datetime import datetime
class UserModel(BaseModel):   
    uid: uuid.UUID 
    username: str
    email: str
    firstname: str
    lastname: str
    is_verified: bool = False
    password_hash: str = Field(exclude=True)
    created_at: datetime 
    updated_at: datetime
    
    model_config = {
        "from_attributes": True
    }

class UserCreateModel(BaseModel):
    username: str = Field(max_length=20)
    email: str = Field(max_length=40)
    firstname: str = Field(max_length=20)
    lastname: str = Field(max_length=20)
    password: str = Field(min_length=6)
    