from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional


class UserCreate(BaseModel):
    email: EmailStr
    password: str

class UserOut(BaseModel):
    id: int
    email: EmailStr
    created_at: datetime
    class Config:
        orm_mode = True

class UserLogin(BaseModel):
    email: EmailStr
    password: str




class PostBase(BaseModel):
    id: int
    title: str
    content: str
    owner_id: int
    owner: UserOut
    published: bool = True

class PostCreate(BaseModel):
    title: str
    content: str

class PostUpdate(PostBase):
    published: bool

class PostOUT(BaseModel):
    Post: PostBase
    votes: int
    class Config:
        orm_mode = True
        from_attributes = True

class PostReturn(BaseModel):
    title: str
    content: str
    class Config:
        orm_mode = True





class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    id: Optional[int] = None



class Vote_Create(BaseModel):
    post_id: int
    dir: bool