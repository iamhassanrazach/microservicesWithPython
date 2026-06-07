import uuid
from datetime import datetime, timezone
from typing import Optional

from pydantic import BaseModel


# ── Request schema ──────────────────────────────────────────────────────────

VALID_ACTIONS = {"played", "completed", "reviewed", "wishlist_added", "started"}


class ActivityCreate(BaseModel):
    user_id: str
    game_id: str
    action: str
    duration_minutes: Optional[int] = None


# ── Enrichment sub-model ────────────────────────────────────────────────────

class GameInfo(BaseModel):
    id: str
    title: str
    genre: Optional[str] = None
    platform: Optional[str] = None
    cover_url: Optional[str] = None


# ── Response schema ─────────────────────────────────────────────────────────

class ActivityResponse(BaseModel):
    id: str
    user_id: str
    game_id: str
    action: str
    duration_minutes: Optional[int] = None
    created_at: str
    game: Optional[GameInfo] = None


# ── In-memory store (replaces DB for this module) ──────────────────────────

_store: list[dict] = []


def save_activity(data: ActivityCreate) -> dict:
    record = {
        "id": str(uuid.uuid4()),
        "user_id": data.user_id,
        "game_id": data.game_id,
        "action": data.action,
        "duration_minutes": data.duration_minutes,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    _store.append(record)
    return record


def list_activities(limit: int = 20, offset: int = 0) -> list[dict]:
    return _store[offset: offset + limit]


def list_activities_by_user(user_id: str, limit: int = 20, offset: int = 0) -> list[dict]:
    filtered = [a for a in _store if a["user_id"] == user_id]
    return filtered[offset: offset + limit]
