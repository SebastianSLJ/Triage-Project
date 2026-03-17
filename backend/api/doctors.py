from fastapi import HTTPException, APIRouter, status, Depends
from typing import List
from ..api.dependencies import get_current_user
from ..db.base import User, Doctor, UserRole
from ..db.session import get_db
from sqlalchemy.orm import Session
from ..schemas.doctor import DoctorProfile, DoctorProfileOut, PatientOut, MessageOut


router = APIRouter()

def denied_access(user: User, requierd_role: UserRole):    
    if user.role!=requierd_role:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Access Denied: This action requires the {required_role} value"
        ) 

@router.post(
    '/profile_update',
    status_code=status.HTTP_201_CREATED,
    tags=['Doctors'],
    summary='Doctor profile completion',    
    description='Completes the doctor profile with specified data',
    response_model=MessageOut   
)
def profile(doctor_data: DoctorProfile, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):  
    # role validation
    denied_access(current_user, UserRole.DOCTOR)
    existing_profile = db.query(Doctor).filter(Doctor.user_id==current_user.id).first()
    if existing_profile:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail='Doctor already exists'
        )
    # Complete the doctor profile using the pydantic model to verify de data entry (Specific fields - speciality, medical_license)
    new_doctor = Doctor(
        user_id = current_user.id,
        speciality = doctor_data.speciality,
        medical_license = doctor_data.medical_license
    )
    db.add(new_doctor)
    db.commit()
    db.refresh(new_doctor)

    return {'message': 'Profile succesfully updated'}


@router.get('/me', response_model=DoctorProfileOut, tags=['Doctors'])
def read_doctors_info(current_user: User = Depends(get_current_user)):
    # If user is a doctor but has not completed his profile, 
    # doctor_profile will show 'none' in this field (doctor Schema defined)
    denied_access(current_user, UserRole.DOCTOR)
    return current_user

@router.get('/patients', response_model=List[PatientOut], tags=['Doctors'])
def read_doctor_patient(current_user: User = Depends(get_current_user)):
    """
    Show doctor patients as a list (json arrays)
    Search for current_user and if is doctor, bring his patients (base relationship)
    """
    if current_user.doctor_profile is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Doctor profile not completed. Please fill your professional data first."
        )
    denied_access(current_user, UserRole.DOCTOR)
    return current_user.doctor_profile.patients
