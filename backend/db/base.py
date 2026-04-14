import enum
from sqlalchemy import ForeignKey, String, Column, Integer, Enum, DateTime, Text, Float, Boolean, Table
from sqlalchemy.orm import DeclarativeBase, relationship
from sqlalchemy.sql import func

# Base class for inheritance (DeclarativeBase) - SQL Statements
class Base(DeclarativeBase):
    pass

class UserRole(enum.Enum):
    DOCTOR = 'doctor'
    PATIENT = 'patient'

class UserGender(enum.Enum):
    MALE = 'Male'
    FEMALE = 'Female'

class PriorityEnum(enum.IntEnum):
    ONE = 1
    TWO = 2
    THREE = 3
    FOUR = 4
    FIVE = 5

class UserState(enum.Enum):
    ACTIVE = "ACTIVE"
    PENDING = "PENDING"

# Users table
class User(Base):
    __tablename__   = 'users'
    id = Column(Integer, primary_key=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    DNI = Column(String(20), unique=True, nullable=False)
    state = Column(Enum(UserState), nullable=False, default=UserState.PENDING)
    role = Column(Enum(UserRole), nullable=False)
    is_active = Column(Boolean, default=True)
    birthdate = Column(DateTime, nullable=False)
    gender = Column(Enum(UserGender), nullable=False)
    created_at = Column(DateTime, server_default=func.now())

    # Relations
    patient_profile = relationship("Patient", back_populates="user", uselist=False)
    doctor_profile = relationship("Doctor", back_populates="user", uselist=False)


# Intermediate table for Patient and Doctor intermediate
class DoctorPatient(Base):
    __tablename__ = 'doctor_patient'    
    doctor_id = Column(Integer, ForeignKey('doctors.id'), primary_key=True)
    patient_id = Column(Integer, ForeignKey('patients.id'), primary_key=True)    
    
    created_at = Column(DateTime, server_default=func.now())
    is_active = Column(Boolean, default=True)

    # Relaciones hacia los modelos originales
    doctor = relationship("Doctor", back_populates="patient_associations")
    patient = relationship("Patient", back_populates="doctor_associations")

class Doctor(Base):
    __tablename__ = 'doctors'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    doctor_name = Column(String(255), nullable=False) 
    speciality = Column(String(100))
    medical_license = Column(String(100), unique=True)

    user = relationship('User', back_populates='doctor_profile')
    triages = relationship('Triage', back_populates='doctor')    
    patient_associations = relationship("DoctorPatient", back_populates="doctor")

class Patient(Base):
    __tablename__ = 'patients'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    name = Column(String(255), nullable=False)    
    # Relations 
    user = relationship('User', back_populates='patient_profile')
    doctor_associations = relationship("DoctorPatient", back_populates="patient")
    triages = relationship('Triage', back_populates='patient')

class Triage(Base):
    __tablename__='triage'

    id = Column(Integer, primary_key=True)
    patient_id = Column(Integer, ForeignKey('patients.id'), nullable=False)
    doctor_id = Column(Integer, ForeignKey('doctors.id'),nullable=False)
    created_at = Column(DateTime, server_default=func.now())

    # Entries for UML Model 
    description = Column(Text, nullable=False)
    symptoms = Column(Text, nullable=False)
    HR = Column(Integer) # Heart Rate
    spo2 = Column(Integer) # Peripheral Oxygen Saturation
    temperature = Column(Float) 
    SBP = Column(Integer) # Systolic Blood Pressure
    RR = Column(Integer) # Respiratory Rate
    duration_hours = Column(Float)
    severe_history = Column(Integer)    

    # Results
    priority = Column(Enum(PriorityEnum), nullable=False)
    doctor_notes = Column(Text, nullable=True)

    #Relations 
    patient = relationship('Patient', back_populates='triages')
    doctor = relationship('Doctor', back_populates='triages')

