from pydantic import BaseModel, ConfigDict

class MessageOut(BaseModel):
    message: str


class TriageCreateRequest(BaseModel): 
    patient_DNI: str  
    description: str
    symptoms: str
    HR: int
    spo2: int 
    temperature: float
    SBP: int 
    duration_hours: float
    RR: int
    duration_hours: float
    severe_history: int    
    model_config = ConfigDict(from_attributes=True)

class PatientCondition(BaseModel):
    name: str
    gender: str
    age: int
    description: str
    symptoms: str
    HR: int
    spo2: int 
    temperature: float
    SBP: int     
    RR: int
    duration_hours: float
    severe_history: int
    model_config = ConfigDict(from_attributes=True)


