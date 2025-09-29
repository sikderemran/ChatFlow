import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database import Base, get_db
from app.main import app

# Use MySQL test database
SQLALCHEMY_TEST_DATABASE_URL = "mysql+pymysql://root:password@auth-test-db:3306/auth_test_db"

engine = create_engine(SQLALCHEMY_TEST_DATABASE_URL)
Base.metadata.create_all(bind=engine)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Override the dependency
def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

# Create tables
Base.metadata.create_all(bind=engine)

client = TestClient(app)

def test_register_and_login():
    # Register
    res = client.post("/register", json={"username": "testuser", "password": "secret"})
    assert res.status_code == 200
    data = res.json()
    assert data["username"] == "testuser"

    # Login
    res = client.post("/login", json={"username": "testuser", "password": "secret"})
    assert res.status_code == 200
    data = res.json()
    assert "access_token" in data

# Optional: clean up after test
@pytest.fixture(scope="session", autouse=True)
def cleanup():
    yield
    Base.metadata.drop_all(bind=engine)
