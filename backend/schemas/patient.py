from pydantic import BaseModel, EmailStr, ConfigDict
from datetime import date
from ..db.base import UserGender
from .doctor import DoctorProfile, UserBasicInfo


class MessageOut(BaseModel):
    message: str

class PatientProfile(BaseModel):
    name: str
    email: EmailStr
    birthdate: date
    gender: UserGender
    
class PatientProfileOut(BaseModel):
    name: str
    user: UserBasicInfo
    birthdate: date
    gender: UserGender
    doctor: DoctorProfile | None = None
    model_config = ConfigDict(from_attributes=True)

    