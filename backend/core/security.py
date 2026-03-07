from datetime import datetime, timedelta, timezone
from passlib.context import CryptContext
from dotenv import load_dotenv
import os
import jwt


load_dotenv()

SECRET_KEY = os.getenv('SECRET_KEY')
ALGORITHM = os.getenv('ALGORITHM')
ACCESS_TOKEN_EXPIRE_MINUTES = os.getenv('ACCESS_TOKEN_EXPIRE_MINUTES')


pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')

def get_password_hash(password: str)->str:
    """Plain password to hashed password"""
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str)->bool:
    """Compare and verify if both password match"""
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict):
    """
    Generates a signed token that the client will use to authenticate.
    """
    to_encode = data.copy()

    # Calculate the expiration time 
    expire = datetime.now(timezone.utc)+timedelta(minutes=int(ACCESS_TOKEN_EXPIRE_MINUTES))

    # Add expiration "payload" (Token body)
    to_encode.update({'exp': expire})

    # Sign the token with SECRET_KEY
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

    return encoded_jwt