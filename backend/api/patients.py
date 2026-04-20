from fastapi import HTTPException, APIRouter, status, Depends
from ..db.base import User, UserRole, Patient, DoctorPatient
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
        description='Complete patient profile with specific data - Onyl Doctor user can modify this information',
        response_model=MessageOut              
    )
def patient_register(patient_data: PatientProfile, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    # Validates the user role that creates complements the patient info (Must be a Doctor)    
    denied_access(current_user, UserRole.DOCTOR)
    # Validates that doctor´s profile is complete 
    if not current_user.doctor_profile:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail='Doctor profile not found. Please fill your professional data first.'
        )
    

    # Search user for DNI (Unique Identifier legal) and validates
    target_user = db.query(User).filter(User.DNI==patient_data.DNI).first()
    if not target_user:
        target_user = User(
            DNI=patient_data.DNI,
            role=UserRole.PATIENT,
            is_active=False,  # Account with no propietary
            email=None,       
            hashed_password=None,  
            birthdate=None,
            gender=None   
        )
        db.add(target_user)
        db.flush()
      
    # Obtain or Create the patient profile
    patient_profile = db.query(Patient).filter(Patient.user_id == target_user.id).first()
    
    if not patient_profile:
        patient_profile = Patient(user_id=target_user.id, name=patient_data.name, DNI=patient_data.DNI)
        db.add(patient_profile)
        db.flush() # Obtain the id whitout close the transaction

    # Vinculates the doctor using the intermediate relation (table intermeadiate)
    # First, verify if there are vinculation already
    existing_relation = db.query(DoctorPatient).filter(
        DoctorPatient.doctor_id == current_user.doctor_profile.id,
        DoctorPatient.patient_id == patient_profile.id
    ).first()

    if existing_relation:
        if existing_relation.is_active:
            raise HTTPException(status_code=400, detail='The patient was already in his care')
        else:
            # If it exists but was inactive, we reactivate it
            existing_relation.is_active = True
    else:
        # create the new association
        new_association = DoctorPatient(
            doctor_id=current_user.doctor_profile.id,
            patient_id=patient_profile.id,
            is_active=True
        )
        db.add(new_association)

    db.commit()
    return {'message': 'Pacient vinculated succesfully'}

@router.get('/me', response_model=PatientProfileOut, tags=['Patients'], description='Patient user can see his data and history')
def read_patient_self_info(current_user: User = Depends(get_current_user)):
    if current_user.role != UserRole.PATIENT:
        raise HTTPException(status_code=403, detail="Access denied: You are not a patient")    
    if not current_user.patient_profile:
        raise HTTPException(status_code=404, detail="Patient profile not found")        
    return current_user.patient_profile