from fastapi import HTTPException, APIRouter, status, Depends
from fastapi.security import OAuth2PasswordRequestForm
from ..schemas.user import UserRegister, UserRole, MessageResponse
from sqlalchemy.orm import Session
from ..db.session import get_db
from ..db.base import User, UserState
from ..core.security import get_password_hash, verify_password, create_access_token

router = APIRouter()


@router.post(
    # Path
    '/registration',
    # Define qué datos verá el cliente (oculta la contraseña)
    response_model=MessageResponse,
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
def registration(data: UserRegister, db: Session = Depends(get_db)):
    """
    Registrates a new user    
    
    Verify that email doesn't exist previously and create a base 
    identity with the specified role.
    """
    #User searching (Early return)    
    existing_user = db.query(User).filter(User.DNI== data.DNI).first()

    if existing_user:
        # Case A: The account is already active (Someone already use this DNI with this email)
        if existing_user.email is not None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, 
                detail="Este DNI ya tiene una cuenta activa vinculada."
            )
        
        # Case B: Uncreated account (Only created by a doctor for Triage association)
        # Here the user can take an created account created by a doctor (Using his DNI and email - Coincidence)
        existing_user.email = data.email
        hashed_pass = get_password_hash(data.password)
        existing_user.hashed_password = hashed_pass
        existing_user.birthdate = data.birthdate
        existing_user.gender = data.gender
        existing_user.is_active = True # Activate the account so the user can login 
        existing_user.state = UserState.ACTIVE
        db.commit()
        return {"message": "Cuenta activada y vinculada exitosamente"}
        
    # Case C: The DNI doesn't exist at all (Traditional Register)
    # Verify if the email isn't taken already by another DNI
    email_check = db.query(User).filter(User.email == data.email).first()
    if email_check:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El correo electrónico ya está en uso."
        )

    new_user = User(
        DNI=data.DNI,
        email=data.email,
        hashed_password=hashed_pass,
        birthdate=data.birthdate,
        gender=data.gender,
        role=UserRole.PATIENT,
        state=UserState.ACTIVE,
        is_active=True        
    )
    
    db.add(new_user)
    db.commit()
    return {"message": "Usuario registrado exitosamente"}
    

@router.post('/login',summary='Login and Token get',tags=["Authentication"])
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
