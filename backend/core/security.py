from datetime import datetime, timedelta, timezone
from passlib.context import CryptContext
import jwt
from .config import settings


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
    to_encode = data.copy() # dict

    # Calculate the expiration time 
    expire = datetime.now(timezone.utc)+timedelta(minutes=int(settings.ACCESS_TOKEN_EXPIRE_MINUTES))

    # Add expiration "payload" (Token body)
    to_encode.update({'exp': expire})

    # Sign the token with SECRET_KEY
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

    return encoded_jwt