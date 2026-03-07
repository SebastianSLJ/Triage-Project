from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, query
from dotenv import load_dotenv
import os

load_dotenv()

# .env variables for URI
DB_USER = os.getenv('DB_USER')
DB_PASSWORD = os.getenv('DB_PASSWORD')
DB_NAME = os.getenv('DB_NAME')
DB_PORT = os.getenv('DB_PORT')
DB_HOST = os.getenv('DB_HOST')
# URI for DB conection
DB_URI = f'postgresql+psycopg://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}'

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
    except:
        if session is not None: 
            session.rollback()
        raise
    finally:
        if session: 
            session.close()