from pydantic import BaseModel, Field

class UserCreateModel(BaseModel):
    username: str = Field(max_length=20)
    email: str=Field(max_length=20)
    password: str = Field(min_length=6)