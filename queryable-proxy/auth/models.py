from pydantic import BaseModel, EmailStr
from typing import Optional

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None
    
class UserBase(BaseModel):
    email: EmailStr
    is_active: bool = True
    
class UserCreate(UserBase):
    password: str
    
class User(UserBase):
    id: int
    tier: str = "basic"  # e.g., "basic", "premium", "enterprise"
    
    class Config:
        from_attributes = True
