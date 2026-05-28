from sqlalchemy.orm import Session
from app.models import Activity
from app.schemas import ActivityCreate


def create_activity(db: Session, data: ActivityCreate) -> Activity:
    activity = Activity(
        user_id=data.user_id,
        game_id=data.game_id,
        action=data.action,
        duration_minutes=data.duration_minutes,
    )
    db.add(activity)
    db.commit()
    db.refresh(activity)
    return activity


def get_activity(db: Session, activity_id: str) -> Activity | None:
    return db.query(Activity).filter(Activity.id == activity_id).first()


def list_activities(db: Session, limit: int = 20, offset: int = 0):
    total = db.query(Activity).count()
    items = db.query(Activity).order_by(Activity.created_at.desc()).offset(offset).limit(limit).all()
    return items, total


def list_activities_by_user(db: Session, user_id: str, limit: int = 20, offset: int = 0):
    q = db.query(Activity).filter(Activity.user_id == user_id)
    total = q.count()
    items = q.order_by(Activity.created_at.desc()).offset(offset).limit(limit).all()
    return items, total
