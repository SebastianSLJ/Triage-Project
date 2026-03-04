from pydantic import BaseModel, EmailStr
from ..db.base import UserRole


# Pydantic models for user data insertion 
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

