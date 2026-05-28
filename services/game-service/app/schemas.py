from __future__ import annotations
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel


class GameCreate(BaseModel):
    title: str
    genre: str
    platform: str
    release_year: Optional[int] = None
    cover_url: Optional[str] = None


class GameOut(BaseModel):
    id: str
    title: str
    genre: str
    platform: str
    release_year: Optional[int]
    cover_url: Optional[str]
    created_at: datetime

    model_config = {"from_attributes": True}


class GameList(BaseModel):
    items: List[GameOut]
    total: int
    limit: int
    offset: int