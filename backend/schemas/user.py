from pydantic import BaseModel, EmailStr
from ..db.base import UserRole

class UserCreate(BaseModel):
    email: EmailStr
    password: str
    role: UserRole

class UserOut(BaseModel):
    id: int 
    email: EmailStr
    role: UserRole
    is_active: bool 
    class Config:
        from_attributes = True

