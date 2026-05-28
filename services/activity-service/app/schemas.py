from __future__ import annotations
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel


# ── inbound ──────────────────────────────────────────────────────────────────

class ActivityCreate(BaseModel):
    user_id:          str
    game_id:          str
    action:           str   # played | completed | reviewed | wishlist_added
    duration_minutes: Optional[int] = None


# ── game snapshot embedded in response ───────────────────────────────────────

class GameSummary(BaseModel):
    id:        str
    title:     str
    genre:     str
    platform:  str
    cover_url: Optional[str] = None


# ── outbound ─────────────────────────────────────────────────────────────────

class ActivityOut(BaseModel):
    id:               str
    user_id:          str
    action:           str
    duration_minutes: Optional[int]
    created_at:       datetime
    game:             Optional[GameSummary] = None

    model_config = {"from_attributes": True}


class ActivityList(BaseModel):
    items:  List[ActivityOut]
    total:  int
    limit:  int
    offset: int
