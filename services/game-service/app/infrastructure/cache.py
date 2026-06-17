# Module 5 — CQRS read model.
#
# SQLite is the write model (authoritative). Redis is the read model (fast, potentially stale).
#
# Write side (set_game_summary): call it from service.add_game() after the game
#   is saved to SQLite.
# Read side (get_game_summary): used by GET /v1/games/{id}/summary in routes.py.

import json

import redis

from app.config import settings

_client: redis.Redis | None = None


def _get_client() -> redis.Redis:
    global _client
    if _client is None:
        _client = redis.from_url(settings.redis_url, decode_responses=True)
    return _client


def _key(game_id: str) -> str:
    return f"game:summary:{game_id}"


# ---------------------------------------------------------------------------
# Write side — call this from service.py after creating a game
# ---------------------------------------------------------------------------

def set_game_summary(game_id: str, data: dict) -> None:
    """
    Store a game summary projection in Redis.

    data must match the /summary response shape from api-contracts.md:
        { "id": "...", "title": "...", "genre": "...", "platform": "...", "cover_url": "..." }
    """
    r = _get_client()
    r.set(_key(game_id), json.dumps(data))


# ---------------------------------------------------------------------------
# Read side
# ---------------------------------------------------------------------------

def get_game_summary(game_id: str) -> dict | None:
    """
    Retrieve a game summary projection from Redis.

    Returns the cached dict if the key exists, or None if it was never cached
    (e.g. the game was added before Redis was running).
    """
    r = _get_client()
    raw = r.get(_key(game_id))
    if raw is None:
        return None
    return json.loads(raw)
