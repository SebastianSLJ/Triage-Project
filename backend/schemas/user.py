from pydantic import BaseModel, EmailStr
from ..db.base import UserRole, UserGender
from datetime import date

class MessageResponse(BaseModel):
    message: str

# Pydantic models for user data insertion (Registration)
class UserRegister(BaseModel):
    DNI: str 
    email: EmailStr
    password: str
    birthdate: date
    gender: UserGender
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
