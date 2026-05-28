import httpx
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import Base, engine, get_db
from app.schemas import ActivityCreate, ActivityOut, ActivityList, GameSummary
from app import repository

Base.metadata.create_all(bind=engine)

app = FastAPI(title="activity-service", version="1.0.0")

USER_SERVICE_URL = "http://localhost:8001"
GAME_SERVICE_URL = "http://localhost:8002"


async def validate_user(user_id: str) -> None:
    url = f"{USER_SERVICE_URL}/v1/users/{user_id}"
    for attempt in range(1, 4):
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                resp = await client.get(url)
            if resp.status_code == 404:
                raise HTTPException(status_code=404, detail="User not found")
            if resp.status_code == 200:
                return
            if attempt == 3:
                raise HTTPException(status_code=502, detail="user-service error")
        except HTTPException:
            raise
        except httpx.RequestError:
            if attempt == 3:
                raise HTTPException(status_code=503, detail="user-service unavailable")


async def fetch_game_data(game_id: str) -> GameSummary | None:
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            resp = await client.get(f"{GAME_SERVICE_URL}/v1/games/{game_id}")
        if resp.status_code == 200:
            data = resp.json()
            return GameSummary(
                id=data["id"],
                title=data["title"],
                genre=data["genre"],
                platform=data["platform"],
                cover_url=data.get("cover_url"),
            )
        return None
    except httpx.RequestError:
        return None


@app.post("/v1/activities", response_model=ActivityOut, status_code=201)
async def create_activity(data: ActivityCreate, db: Session = Depends(get_db)):
    await validate_user(data.user_id)
    activity = repository.create_activity(db, data)
    game = await fetch_game_data(data.game_id)
    out = ActivityOut.model_validate(activity)
    out.game = game
    return out


@app.get("/v1/activities", response_model=ActivityList)
async def list_activities(limit: int = 20, offset: int = 0, db: Session = Depends(get_db)):
    items, total = repository.list_activities(db, limit=limit, offset=offset)
    enriched = []
    for activity in items:
        game = await fetch_game_data(activity.game_id)
        out = ActivityOut.model_validate(activity)
        out.game = game
        enriched.append(out)
    return ActivityList(items=enriched, total=total, limit=limit, offset=offset)


@app.get("/v1/activities/user/{user_id}", response_model=ActivityList)
async def list_user_activities(user_id: str, limit: int = 20, offset: int = 0, db: Session = Depends(get_db)):
    items, total = repository.list_activities_by_user(db, user_id, limit=limit, offset=offset)
    enriched = []
    for activity in items:
        game = await fetch_game_data(activity.game_id)
        out = ActivityOut.model_validate(activity)
        out.game = game
        enriched.append(out)
    return ActivityList(items=enriched, total=total, limit=limit, offset=offset)


@app.get("/health")
def health():
    return {"status": "ok", "service": "activity-service"}