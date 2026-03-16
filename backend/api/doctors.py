from fastapi import HTTPException, APIRouter, status, Depends
from typing import List
from ..api.dependencies import get_current_user
from ..db.base import User, Doctor, UserRole
from ..db.session import get_db
from sqlalchemy.orm import Session
from ..schemas.doctor import DoctorProfile, DoctorProfileOut, PatientOut


router = APIRouter()

@router.post(
    '/profile_update',
    status_code=status.HTTP_201_CREATED,
    tags=['Doctors'],
    summary='Doctor profile completion',    
    description='Completes the doctor profile with specified data'    
)
def profile(doctor_data: DoctorProfile, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):  
    # role validation
    if current_user.role!=UserRole.DOCTOR: 
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail='Access Denied: The user is not a Doctor'
        )
    existing_profile = db.query(Doctor).filter(Doctor.user_id==current_user.id).first()
    if existing_profile:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail='Doctor already exists'
        )
    new_doctor = Doctor(
        user_id = current_user.id,
        speciality = doctor_data.speciality,
        medical_license = doctor_data.medical_license
    )
    db.add(new_doctor)
    db.commit()
    db.refresh(new_doctor)

    return {'message': 'Succesfully completed profile'}

@router.get('/me', response_model=DoctorProfileOut)
def read_doctors_info(current_doctor: User = Depends(get_current_user)):
    # If user is a doctor but has not completed his profile, 
    # doctor_profile will show none in this field (doctor Schema defined)
    return current_doctor

@router.get('/patients', response_model=List[PatientOut])
def read_doctor_patient(current_user: User = Depends(get_current_user)):
    if current_user.role!= UserRole.DOCTOR:
        raise HTTPException(status_code=403, detail='Not Authorized')
    return current_user.doctor_profile.patients
