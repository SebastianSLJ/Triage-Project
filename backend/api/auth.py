from fastapi import HTTPException, APIRouter, status, Depends
from fastapi.security import OAuth2PasswordRequestForm
from ..schemas.user import UserCreate, UserOut
from sqlalchemy.orm import Session
from ..db.session import get_db
from ..db.base import User
from ..core.security import get_password_hash, verify_password, create_access_token
from ..api.dependencies import get_current_user

router = APIRouter()


@router.post(
    # Path
    '/registration',
    # Define qué datos verá el cliente (oculta la contraseña)
    response_model=UserOut,
    # El código 201 indica que un recurso fue creado con éxito
    status_code=status.HTTP_201_CREATED,
    # Estas etiquetas agrupan tus rutas en la documentación /docs
    tags=["Authentication"],
    # Un resumen corto que aparece en la lista de Swagger
    summary="New user registration",
    # Una descripción detallada que explica reglas de negocio
    description="Create an user in DB. The profile (Doctor/Pacient) must be completed after"
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
    hashed_pass = get_password_hash(user.password)

    # User instance for commit user
    new_user = User(
        email=user.email, 
        hashed_password=hashed_pass, 
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

@router.post('/login',summary='Login and Token get')
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """
    1. Search user by email
    2. Compare plain password with hashed password in DB
    3. Validate, generate and return JWT Token 
    """
    # 1. Search for user (filter by email and compare with the email entrance in login)
    user = db.query(User).filter(User.email == form_data.username).first()
    # 2. Verify the password using the function in security
    if not user or not verify_password(form_data.password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail='Incorrect email or password',
                headers={"WWW-Authenticate": "Bearer"}
            )
    # 3. Generate the token 
    # Save email in subject field in JWT
    access_token = create_access_token(data={'sub': user.email})
    return{
        'access_token': access_token,
        'token_type': 'bearer'
    }

@router.get("/me", response_model=UserOut)
def read_users_me(current_user: User = Depends(get_current_user)):
    """
    Si llegamos aquí, es porque el 'Depends' hizo toda la magia:
    validó el token, buscó en la DB y nos entregó el objeto usuario.
    """
    return current_user