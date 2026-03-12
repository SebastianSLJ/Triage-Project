from pydantic import BaseModel, EmailStr
from ..db.base import UserRole

class DoctorProfileUpdate(BaseModel):
    speciality: str
    medical_license: str