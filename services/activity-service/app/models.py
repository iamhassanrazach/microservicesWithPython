import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Integer, DateTime
from app.database import Base


def _uuid():
    return str(uuid.uuid4())


def _now():
    return datetime.now(timezone.utc)


class Activity(Base):
    __tablename__ = "activities"

    id               = Column(String, primary_key=True, default=_uuid)
    user_id          = Column(String, nullable=False, index=True)
    game_id          = Column(String, nullable=False)
    action           = Column(String, nullable=False)   # played | completed | reviewed | wishlist_added
    duration_minutes = Column(Integer, nullable=True)
    created_at       = Column(DateTime(timezone=True), default=_now)
