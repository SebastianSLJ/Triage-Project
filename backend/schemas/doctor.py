from pydantic import BaseModel, ConfigDict
from ..db.base import UserRole

class DoctorProfile(BaseModel):
    speciality: str
    medical_license: str

class DoctorProfileOut(BaseModel):
    email: str
    role: UserRole
    is_active: bool
    doctor_profile: DoctorProfile | None = None
    model_config = ConfigDict(from_attributes=True)

class PatientOut(BaseModel):
    name: str
    birthdate: str
    gender: str
    email: str
    is_active: bool
    model_config = ConfigDict(from_attributes=True)
