from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from ..core.config import settings

DB_URI = f'postgresql+psycopg://{settings.DB_USER}:{settings.DB_PASSWORD}@{settings.DB_HOST}:{settings.DB_PORT}/{settings.DB_NAME}'

# URI creation for engine object (DB conection)
engine = create_engine(
    DB_URI,
    echo = True
)

Session = sessionmaker(bind=engine, autoflush=False, autocommit=False)

# get_db function for create session 
def get_db():
    session = None
    try:
        session = Session()
        yield session       
    except Exception:
        session.rollback()
        raise
    finally:
        if session: 
            session.close()