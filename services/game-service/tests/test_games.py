import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.database import Base, get_db

SQLALCHEMY_TEST_URL = "sqlite:///./test_games.db"

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


def test_create_game_returns_201():
    response = client.post("/v1/games/", json={
        "title": "Hollow Knight",
        "genre": "metroidvania",
        "platform": "PC",
        "release_year": 2017,
        "cover_url": "https://example.com/hk.jpg"
    })
    assert response.status_code == 201
    body = response.json()
    assert body["title"] == "Hollow Knight"
    assert body["genre"] == "metroidvania"
    assert "id" in body
    assert "created_at" in body


def test_get_game_returns_200():
    created = client.post("/v1/games/", json={
        "title": "Celeste",
        "genre": "platformer",
        "platform": "PC"
    }).json()
    response = client.get(f"/v1/games/{created['id']}")
    assert response.status_code == 200
    assert response.json()["title"] == "Celeste"


def test_get_unknown_game_returns_404():
    response = client.get("/v1/games/nonexistent-id")
    assert response.status_code == 404


def test_list_games_returns_paginated_envelope():
    client.post("/v1/games/", json={"title": "Game A", "genre": "rpg", "platform": "PC"})
    client.post("/v1/games/", json={"title": "Game B", "genre": "rpg", "platform": "PS5"})
    response = client.get("/v1/games/")
    assert response.status_code == 200
    body = response.json()
    assert body["total"] == 2
    assert len(body["items"]) == 2
    assert "limit" in body
    assert "offset" in body


def test_search_games_filters_by_title():
    client.post("/v1/games/", json={"title": "Dark Souls", "genre": "action-rpg", "platform": "PC"})
    client.post("/v1/games/", json={"title": "Hollow Knight", "genre": "metroidvania", "platform": "PC"})
    response = client.get("/v1/games/search?q=dark")
    assert response.status_code == 200
    body = response.json()
    assert body["total"] == 1
    assert body["items"][0]["title"] == "Dark Souls"
