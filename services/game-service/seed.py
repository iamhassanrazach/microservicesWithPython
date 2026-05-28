import sys, os
sys.path.insert(0, os.path.dirname(__file__))

from app.database import SessionLocal, engine
from app.models import Game, Base
import uuid

Base.metadata.create_all(bind=engine)

GAMES = [
    {"title": "Hollow Knight",  "genre": "metroidvania", "platform": "PC",  "release_year": 2017, "cover_url": "https://example.com/hollow-knight.jpg"},
    {"title": "Celeste",        "genre": "platformer",   "platform": "PC",  "release_year": 2018, "cover_url": "https://example.com/celeste.jpg"},
    {"title": "Hades",          "genre": "roguelike",    "platform": "PC",  "release_year": 2020, "cover_url": "https://example.com/hades.jpg"},
    {"title": "The Witcher 3",  "genre": "rpg",          "platform": "PC",  "release_year": 2015, "cover_url": "https://example.com/witcher3.jpg"},
    {"title": "Stardew Valley", "genre": "simulation",   "platform": "PC",  "release_year": 2016, "cover_url": "https://example.com/stardew.jpg"},
    {"title": "God of War",     "genre": "action",       "platform": "PS5", "release_year": 2022, "cover_url": "https://example.com/gow.jpg"},
    {"title": "Elden Ring",     "genre": "soulslike",    "platform": "PC",  "release_year": 2022, "cover_url": "https://example.com/elden-ring.jpg"},
    {"title": "Disco Elysium",  "genre": "rpg",          "platform": "PC",  "release_year": 2019, "cover_url": "https://example.com/disco.jpg"},
]

def seed():
    db = SessionLocal()
    inserted = 0
    try:
        for g in GAMES:
            exists = db.query(Game).filter(Game.title == g["title"]).first()
            if not exists:
                db.add(Game(id=str(uuid.uuid4()), **g))
                inserted += 1
        db.commit()
        print(f"Seeded {inserted} games ({len(GAMES) - inserted} already existed).")
    finally:
        db.close()

if __name__ == "__main__":
    seed()