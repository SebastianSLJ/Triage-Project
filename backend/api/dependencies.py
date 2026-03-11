from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from ..db.session import get_db
from ..db.base import User
import jwt
from ..core.config import settings
from jwt import PyJWTError as JWTError


# Search the token on login endpoint
oauth2_scheme = OAuth2PasswordBearer(tokenUrl='api/auth/login')

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    """Decode the token received from login endpoint
        Decode the token for verify its authenticity (SECRET_KEY)
        Extract the email searching for 'sub' (subject) in token ('sub': email)
        Search in database for bring the user credentials 
        return user
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail='The credentials could not be validated',
        headers={"WWW-Authenticate": "Bearer"}          
    )
    try:
        # Decoding
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=settings.ALGORITHM)
        # extract email from payload 'subject'
        email: str= payload.get('sub')
        if email is None: 
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    user = db.query(User).filter(User.email==email).first()
    if user is None:
        raise credentials_exception
    return user

