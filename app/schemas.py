from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional, List


class PostReturn(BaseModel):
    title: str
    content: str
    class Config:
        orm_mode = True

class UserCreate(BaseModel):
    email: EmailStr
    password: str

class UserOut(BaseModel):
    email: EmailStr
    posts: List[PostReturn]
    class Config:
        orm_mode = True

class UserLogin(BaseModel):
    email: EmailStr
    password: str





class CommentBase(BaseModel):
    post_id: int
    content: str
    owner: UserOut

class CommentOut(BaseModel):
    content: str
    owner: UserOut
    class Config:
        orm_mode = True
        from_attributes = True

class CommentUpdate(BaseModel):
    content: str




class PostBase(BaseModel):
    id: int
    title: str
    content: str
    owner_id: int
    owner: UserOut
    published: bool = True
    discussion: List[CommentOut]

class PostCreate(BaseModel):
    title: str
    content: str

class PostUpdate(PostBase):
    published: bool

class PostOUT(BaseModel):
    Post: PostBase
    votes: int
    comms: int
    class Config:
        orm_mode = True
        from_attributes = True






class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    id: Optional[int] = None





class Vote_Create(BaseModel):
    post_id: int
    dir: bool



class UserPublicProfile(BaseModel):
    User: UserOut
    votes: int
    notes: int
    
    class Config:
        from_attributes = True
        orm_mode = True