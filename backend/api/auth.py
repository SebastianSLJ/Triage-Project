from fastapi import Depends, HTTPException, APIRouter, status, Depends
from ..schemas.user import UserCreate, UserOut
from sqlalchemy.orm import Session
from ..db.session import get_db
from ..db.base import User

router = APIRouter()

@router.post(
        '/registration/',
        response_model=UserOut,
        status_code=status.HTTP_201_CREATED
        )
def registration(user: UserCreate, db: Session = Depends(get_db)):

    #User searching (Early return)
    existent_user = db.query(User).filter(User.email == user.email).first()

    if existent_user:
        raise HTTPException(
            status_code=409,
            detail='Email already exists'
        )
    
    # Password Hashing (To-do)

    # User instance for commit user
    new_user = User(
        email=user.email, 
        hashed_password=user.password, 
        role=user.role
        )
    
    # TRANSACTIONS
    # Save
    db.add(new_user)
    db.commit()
    # Object update with DB data
    db.refresh(new_user)

    return new_user



