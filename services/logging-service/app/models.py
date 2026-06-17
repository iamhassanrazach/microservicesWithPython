# Two tables: Consent and ActivityLog.
#
# has_consent() is the gate the RabbitMQ consumer checks before writing
# any log entry — no consent on record (or granted=False) means the
# event is silently discarded.

from datetime import datetime, timezone

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class Consent(db.Model):
    __tablename__ = "consent"

    user_id = db.Column(db.String, primary_key=True)
    granted = db.Column(db.Boolean, nullable=False, default=False)
    updated_at = db.Column(
        db.DateTime,
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )


class ActivityLog(db.Model):
    __tablename__ = "activity_logs"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.String, nullable=False, index=True)
    game_id = db.Column(db.String, nullable=False)
    action = db.Column(db.String, nullable=False)
    message = db.Column(db.String, nullable=True)
    created_at = db.Column(
        db.DateTime,
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )


def has_consent(user_id: str) -> bool:
    """
    Return True if the user has an active consent record with granted=True.
    Return False in all other cases (no record, or granted=False).
    """
    consent = Consent.query.get(user_id)
    if consent is None:
        return False
    return consent.granted
