from pydantic import BaseModel, ConfigDict, EmailStr
from ..db.base import UserRole
from datetime import date

class MessageOut(BaseModel):
    message: str

# We use this class to obtain data (email and is_active) from the table user 
# This data is not in Patient model (sqlaclhemy)
class UserBasicInfo(BaseModel):
    email: EmailStr
    is_active: bool
    model_config = ConfigDict(from_attributes=True)

class DoctorProfile(BaseModel):
    speciality: str
    medical_license: str

class DoctorProfileOut(BaseModel):
    email: EmailStr
    role: UserRole
    is_active: bool
    doctor_profile: DoctorProfile | None = None
    model_config = ConfigDict(from_attributes=True)

class PatientOut(BaseModel):
    name: str
    birthdate: date
    gender: str
    # Acess to another table attributes to complete data (Patients in visualisation endpoint (Doctor))
    user: UserBasicInfo
    model_config = ConfigDict(from_attributes=True)
