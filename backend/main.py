from fastapi import FastAPI
from backend.api.auth import router as auth_router
from backend.api.doctors import router as doctors_router
from backend.db.base import Base
from backend.db.session import engine

Base.metadata.create_all(engine)

app = FastAPI()


@app.get("/")
def root():
    return {"Hello: World"}

app.include_router(auth_router, prefix='/api/auth')
app.include_router(doctors_router, prefix='/api/doctors')