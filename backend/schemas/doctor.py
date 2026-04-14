from pydantic import BaseModel, ConfigDict, EmailStr
from ..db.base import UserRole, UserGender
from datetime import date


# Standard schema for generic API responses.
class MessageOut(BaseModel):
    message: str

# We use this class to obtain data (email and is_active) from the table user 
# This data is not in Patient model (sqlaclhemy)
class PatientBasicInfo(BaseModel):
    name: str
    email: EmailStr
    is_active: bool
    birthdate: date
    gender: UserGender
    model_config = ConfigDict(from_attributes=True)

# Doctor Profile basic information
class DoctorProfile(BaseModel):
    doctor_name: str
    speciality: str
    medical_license: str

# Chart to see only a patient (individual)
class PatientOut(BaseModel):
    user: PatientBasicInfo  
    # Acess to another table attributes to complete data (Patients in visualisation endpoint (Doctor))    
    model_config = ConfigDict(from_attributes=True)

# Intermeadite table for Doctor to see all his patients 
class PatientDoctorAssociationOut(BaseModel):
    is_active: bool
    created_at: date 
    patient: PatientOut     
    model_config = ConfigDict(from_attributes=True)     

# Doctor's chart to view their data and associated patients
class DoctorProfileOut(BaseModel):
    email: EmailStr
    role: UserRole
    is_active: bool
    doctor_profile: DoctorProfile | None = None
    model_config = ConfigDict(from_attributes=True)