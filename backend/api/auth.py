from fastapi import HTTPException, APIRouter, status, Depends
from ..schemas.user import UserCreate, UserOut
from sqlalchemy.orm import Session
from ..db.session import get_db
from ..db.base import User
from ..core.security import get_password_hash

router = APIRouter()


@router.post(
    # Path
    '/registration/',
    # Define qué datos verá el cliente (oculta la contraseña)
    response_model=UserOut,
    # El código 201 indica que un recurso fue creado con éxito
    status_code=status.HTTP_201_CREATED,
    # Estas etiquetas agrupan tus rutas en la documentación /docs
    tags=["authentication"],
    # Un resumen corto que aparece en la lista de Swagger
    summary="Registrar un nuevo usuario",
    # Una descripción detallada que explica reglas de negocio
    description="Crea un usuario base en la DB. El perfil (Médico/Paciente) se debe completar en un paso posterior."
)

# Function for user registration in DB 
def registration(user: UserCreate, db: Session = Depends(get_db)):
    """
    Registra un nuevo usuario en el sistema.
    
    Verifica que el email no exista previamente y crea una identidad base 
    con el rol especificado.
    """
    #User searching (Early return)    
    existent_user = db.query(User).filter(User.email == user.email).first()

    if existent_user:
        raise HTTPException(
            status_code= status.HTTP_409_CONFLICT,
            detail='Email already exists'
        )
    
    #Hash password before create user instance 
    secure_password = get_password_hash(user.password)

    # User instance for commit user
    new_user = User(
        email=user.email, 
        hashed_password=secure_password, 
        role=user.role
        )
    
    # TRANSACTIONS
    # Save
    db.add(new_user)
    db.commit()
    # Object update with DB data
    db.refresh(new_user)
    # Return new_user to watch de created data
    return new_user



