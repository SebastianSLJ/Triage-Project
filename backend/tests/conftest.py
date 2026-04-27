import os
from dotenv import load_dotenv
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '..', '.env'))
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
os.environ["DB_HOST"] = "localhost"

import pytest

from backend.db.base import Base
from fastapi.testclient import TestClient
from backend.main import app
from backend.db.session import get_db

load_dotenv()

# Test database creation (create_engine -> build up database)
TEST_DATABASE_URL = 'postgresql+psycopg://postgres:gary2026@db:5432/mediqueue_test'
engine_test = create_engine(TEST_DATABASE_URL)
TestingSessionLocal = sessionmaker(bind=engine_test, autocommit=False, autoflush=False)

# Fixture (Creation and deletion of tables)
@pytest.fixture(scope="session", autouse=True)
def setup_database():
    '''
scope='session' = Only happens one time in all test session not for each test.
'''
    Base.metadata.create_all(bind=engine_test)
    yield
    Base.metadata.drop_all(bind=engine_test)

# Database session fixture
@pytest.fixture()
def db():
    connection = engine_test.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)
    yield session
    session.close()
    transaction.rollback()
    connection.close()

# Use override to replace get_db from the real database for testing (get_db_test_database)
@pytest.fixture()
def client(db):
    def override_get_db():
        yield db
    
    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)
    app.dependency_overrides.clear()