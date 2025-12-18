from typing import Optional
from pydantic import BaseModel, EmailStr
from src.models.user import UserRole

class UserBase(BaseModel):
    username: str
    email: EmailStr

class UserCreate(UserBase):
    password: str
    role: UserRole = UserRole.STUDENT

class UserLogin(BaseModel):
    username: str
    password: str

class User(UserBase):
    id: int
    role: str
    is_active: bool

    class Config:
        orm_mode = True

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None
    role: Optional[str] = None
