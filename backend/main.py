from fastapi import FastAPI
from backend.api.auth import router as auth_router
from backend.api.doctors import router as doctors_router
from backend.api.patients import router as patients_router
from backend.api.triages import router as triages_router
from backend.api.consultation import router as speciality_consultation
from backend.db.base import Base
from backend.db.session import engine
from fastapi.responses import RedirectResponse

if __name__ == "__main__":
    Base.metadata.create_all(engine)

app = FastAPI()

@app.get('/')
def root():
    return RedirectResponse(url='/docs')

app.include_router(auth_router, prefix='/api/auth')
app.include_router(doctors_router, prefix='/api/doctors')
app.include_router(patients_router, prefix='/api/patients')
app.include_router(triages_router, prefix='/api/triages')
app.include_router(speciality_consultation, prefix='/api/speciality_consultation')