import enum
from sqlalchemy import ForeignKey, String, Column, Integer, Enum, DateTime, Text, Float, Boolean
from sqlalchemy.orm import DeclarativeBase, relationship
from sqlalchemy.sql import func

# Base class for inheritance (DeclarativeBase) - SQL Statements
class Base(DeclarativeBase):
    pass

class UserRole(enum.Enum):
    DOCTOR = 'doctor'
    PATIENT = 'patient'

class PriorityEnum(enum.Enum):
    MILD = 'mild'
    MODERATE = 'moderate'
    SEVERE = 'severe'

# Users table
class User(Base):
    __tablename__   = 'users'
    id = Column(Integer, primary_key=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    role = Column(Enum(UserRole), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now())

    # Relations
    patient_profile = relationship("Patient", back_populates="user", uselist=False)
    doctor_profile = relationship("Doctor", back_populates="user", uselist=False)


class Doctor(Base):
    __tablename__ = 'doctors'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    speciality = Column(String(100))
    medical_license = Column(String(100), unique=True)

    user = relationship('User', back_populates='doctor_profile')
    patients = relationship('Patient', back_populates='doctor')

class Patient(Base):
    __tablename__ = 'patients'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    doctor_id = Column(Integer, ForeignKey('doctors.id'), nullable=True)
    name = Column(String(255), nullable=False)
    birthdate = Column(DateTime)
    gender = Column(String(255))
    
    # Relations 
    user = relationship('User', back_populates='patient_profile')
    doctor = relationship('Doctor', back_populates='patients')
    triages = relationship('Triage', back_populates='patient')

class Triage(Base):
    __tablename__='triage'

    id = Column(Integer, primary_key=True)
    patient_id = Column(Integer, ForeignKey('patients.id'), nullable=False)
    created_at = Column(DateTime, server_default=func.now())

    # Entries for UML Model 
    symptoms = Column(Text, nullable=False)
    heart_rate = Column(Integer)
    blood_pressure = Column(String(20))
    temperature = Column(Float)
    oxygenation = Column(Integer)

    # Results

    priority = Column(Enum(PriorityEnum), nullable=False)
    doctor_notes = Column(Text, nullable=True)

    #Relations 
    patient = relationship('Patient', back_populates='triages')

