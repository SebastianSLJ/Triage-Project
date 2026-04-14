from pydantic import BaseModel, EmailStr, ConfigDict
from datetime import date
from ..db.base import UserGender
from .doctor import DoctorProfile, PatientBasicInfo



class MessageOut(BaseModel):
    message: str

# Patient profile information (For insert in DB)
class PatientProfile(BaseModel):
    name: str
    model_config = ConfigDict(from_attributes=True)
    
# Chart to show Patient profile 
class PatientProfileOut(BaseModel):
    name: str
    user: PatientBasicInfo
    birthdate: date
    gender: UserGender
    doctor: DoctorProfile | None = None
    model_config = ConfigDict(from_attributes=True)

    