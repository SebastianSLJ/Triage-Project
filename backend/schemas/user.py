from pydantic import BaseModel, EmailStr
from ..db.base import UserRole

# Pydantic models for user data insertion (Registration)
class UserCreate(BaseModel):
    email: EmailStr
    password: str
    role: UserRole

# Pydantic model for data visualization (after registration)
class UserOut(BaseModel):
    id: int 
    email: EmailStr
    role: UserRole
    is_active: bool 
    class Config:
        from_attributes = True

# Pydantic model for user login 
class UserLogin(BaseModel):
    email: EmailStr
    password: str

    