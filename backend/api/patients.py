from fastapi import HTTPException, APIRouter, status, Depends
from ..db.base import User, UserRole, Patient
from ..schemas.patient import MessageOut, PatientProfile, PatientProfileOut
from .dependencies import get_current_user
from sqlalchemy.orm import Session
from .doctors import denied_access
from ..db.session import get_db


router = APIRouter()

@router.post(
        '/register',
        status_code=status.HTTP_201_CREATED,
        tags=['Patients'],        
        summary='Patient profile completion',
        description='Complete patient profile with specific data',
        response_model=MessageOut              
    )
def patient_register(patient_data: PatientProfile, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    # Validates the user role that creates complements the patient info (Must be a Doctor)
    denied_access(current_user, UserRole.DOCTOR)
    target_user = db.query(User).filter(User.email==patient_data.email).first()
    if not target_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='No user found with this email. The patient must register an account first'
        )
    # Validates the user role that we're searching (Must be patient)
    denied_access(target_user, UserRole.PATIENT)
    # Validates that doctor´s profile is complete 
    if not current_user.doctor_profile:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail='Doctor profile not found. Please fill your professional data first.'
        )
    # Avoid duplicates
    existing_profile = db.query(Patient).filter(Patient.user_id==target_user.id).first()
    if existing_profile:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail='Patient profile already exists'
        )
    
    new_patient = Patient(
        user_id =  target_user.id,
        doctor_id = current_user.doctor_profile.id,
        name = patient_data.name,
        birthdate = patient_data.birthdate,
        gender = patient_data.gender
    )
    db.add(new_patient)
    db.commit()
    db.refresh(new_patient)
    return {'message': 'Profile succesfully updated'}

@router.get('/me', response_model=PatientProfileOut, tags=['Patients'])
def read_patient_self_info(current_user: User = Depends(get_current_user)):
    if current_user.role != UserRole.PATIENT:
        raise HTTPException(status_code=403, detail="Access denied: You are not a patient")    
    if not current_user.patient_profile:
        raise HTTPException(status_code=404, detail="Patient profile not found")        
    return current_user.patient_profile