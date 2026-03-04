from passlib.context import CryptContext

pwd_context = CryptContext(schemes=['bcrypt'])

def get_password_hash(password: str)->str:
    """Plain password to hashed password"""
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str)->bool:
    """Compare and verify if both password match"""
    return pwd_context.verify(plain_password, hashed_password)