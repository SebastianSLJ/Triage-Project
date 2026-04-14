from fastapi import HTTPException, APIRouter, status, Depends
from ..db.base import User, UserRole, Triage, PriorityEnum
from ..schemas.triage import MessageOut, PatientCondition, TriageCreateRequest
from ..services.triage_service import predict_triage
from .dependencies import get_current_user
from sqlalchemy.orm import Session
from .doctors import denied_access
from ..db.session import get_db
from datetime import datetime

router = APIRouter()

# Function to calculate age from birthdate
def age_calculate(birthdate):
    today = datetime.today()    
    age = today.year - birthdate.year
    if (today.month, today.day) < (birthdate.month, birthdate.day):
        age -= 1
    return age  

@router.post(
    '/triage',
        status_code=status.HTTP_201_CREATED,
        tags=['Patients'],        
        summary='Patient Condition Completed',
        description='Complete the patient status with medical tests and history',
        response_model=MessageOut
)
def create_triage(triage_request: TriageCreateRequest,
    current_user: User = Depends(get_current_user), 
    db: Session = Depends(get_db)
    ):
    # Validates the user role that creates complements the patient info (Must be a Doctor)
    denied_access(current_user, UserRole.DOCTOR)
    
    if not current_user.doctor_profile:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail='Doctor profile not found. Please fill your professional data first.'
        )
    # Search patient by email to validate its existence, age and gender.
    # Search the User and his patient profile 
    target_user = db.query(User).filter(User.email==triage_request.patient_email).first()
    
    if not target_user or not target_user.patient_profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Patient not found or profile not completed.'
        )
    # Calculates the age based on the birthdate
    patient_age = age_calculate(target_user.birthdate)

    # Prepare data for the prediction model
    data_usage = PatientCondition(
        name = target_user.patient_profile.name,
        gender = target_user.gender,  
        age = patient_age,
        description = triage_request.description,
        symptoms = triage_request.symptoms,    
        HR = triage_request.HR,
        spo2 = triage_request.spo2,
        temperature = triage_request.temperature,
        SBP = triage_request.SBP,
        RR = triage_request.RR,
        duration_hours = triage_request.duration_hours,
        severe_history = triage_request.severe_history        
    )
    assigned_priority_num = predict_triage(data_usage)
    # Prediction
    try:
        db_priority = PriorityEnum(assigned_priority_num)
    except ValueError:
    # Por si la IA devuelve algo raro (ej. 0 o 6)
        db_priority = PriorityEnum.FIVE
   
    # Save event on the triage table
    new_triage = Triage(
        patient_id=target_user.patient_profile.id,
        doctor_id=current_user.doctor_profile.id,
        description=triage_request.description,
        symptoms=triage_request.symptoms,
        HR=triage_request.HR,
        spo2=triage_request.spo2,
        temperature=triage_request.temperature,
        SBP=triage_request.SBP,
        RR=triage_request.RR,
        priority=db_priority.value
    )
    db.add(new_triage)
    db.commit()
    db.refresh(new_triage)
    return {'message': 'triage completed'}