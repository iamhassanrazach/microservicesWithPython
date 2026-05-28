import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.database import Base, get_db

SQLALCHEMY_TEST_URL = "sqlite:///./test_users.db"

engine = create_engine(SQLALCHEMY_TEST_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(autouse=True)
def setup_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


client = TestClient(app)


def test_create_user_returns_201():
    response = client.post("/v1/users/", json={
        "username": "nova",
        "email": "nova@example.com",
        "password": "secret"
    })
    assert response.status_code == 201
    body = response.json()
    assert body["username"] == "nova"
    assert body["email"] == "nova@example.com"
    assert "id" in body
    assert "password" not in body


def test_get_user_returns_200():
    created = client.post("/v1/users/", json={
        "username": "atlas",
        "email": "atlas@example.com",
        "password": "pass"
    }).json()
    response = client.get(f"/v1/users/{created['id']}")
    assert response.status_code == 200
    assert response.json()["username"] == "atlas"


def test_get_unknown_user_returns_404():
    response = client.get("/v1/users/nonexistent-id")
    assert response.status_code == 404


def test_list_users_returns_paginated_envelope():
    client.post("/v1/users/", json={"username": "u1", "email": "u1@x.com", "password": "p"})
    client.post("/v1/users/", json={"username": "u2", "email": "u2@x.com", "password": "p"})
    response = client.get("/v1/users/")
    assert response.status_code == 200
    body = response.json()
    assert body["total"] == 2
    assert len(body["items"]) == 2
    assert "limit" in body
    assert "offset" in body
