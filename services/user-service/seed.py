"""
Seed script for user-service.
Idempotent — safe to run multiple times.
Run from services/user-service/:  python seed.py
"""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))

from app.database import SessionLocal, engine
from app.models import User, Base
import hashlib, uuid

Base.metadata.create_all(bind=engine)

USERS = [
    {"username": "nova",    "email": "nova@example.com",    "password": "password"},
    {"username": "pixel",   "email": "pixel@example.com",   "password": "password"},
    {"username": "blaze",   "email": "blaze@example.com",   "password": "password"},
    {"username": "echo",    "email": "echo@example.com",    "password": "password"},
    {"username": "cipher",  "email": "cipher@example.com",  "password": "password"},
]


def fake_hash(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()


def seed():
    db = SessionLocal()
    inserted = 0
    try:
        for u in USERS:
            exists = db.query(User).filter(User.username == u["username"]).first()
            if not exists:
                db.add(User(
                    id=str(uuid.uuid4()),
                    username=u["username"],
                    email=u["email"],
                    hashed_password=fake_hash(u["password"]),
                    is_active=True,
                ))
                inserted += 1
        db.commit()
        print(f"Seeded {inserted} users ({len(USERS) - inserted} already existed).")
    finally:
        db.close()


if __name__ == "__main__":
    seed()
