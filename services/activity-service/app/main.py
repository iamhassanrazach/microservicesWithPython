"""
activity-service — Module 4
============================
Adds asynchronous messaging to the module-03 service.

When an activity is created:
  1. Validate the user exists in user-service  (critical — fail if not found)
  2. Save the activity locally
  3. Publish to RabbitMQ:
       - gamehub.notifications  →  consumed by notification-service
       - gamehub.logs           →  consumed by a future logging-service
  4. Enrich the response with game data from game-service  (optional — null on failure)

The RabbitMQ publish (step 3) is fire-and-forget: if the broker is down,
the activity is still saved and the endpoint returns 201 normally.
"""

import httpx
from fastapi import FastAPI, HTTPException

from app.config import settings
from app.infrastructure.rabbitmq_publisher import publish_message
from app.models import (
    ActivityCreate,
    ActivityResponse,
    GameInfo,
    VALID_ACTIONS,
    list_activities,
    list_activities_by_user,
    save_activity,
)

app = FastAPI(title="activity-service", version="1.0.0")


# ── Health ────────────────────────────────────────────────────────────────

@app.get("/health")
async def health():
    return {"status": "ok", "service": "activity-service"}


# ── Create activity ───────────────────────────────────────────────────────

@app.post("/v1/activities", status_code=201, response_model=ActivityResponse)
async def create_activity(payload: ActivityCreate):
    # Validate action value
    if payload.action not in VALID_ACTIONS:
        raise HTTPException(
            status_code=422,
            detail=f"Invalid action '{payload.action}'. Valid: {sorted(VALID_ACTIONS)}",
        )

    # ── Step 1: validate user (critical) ──────────────────────────────────
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            user_resp = await client.get(
                f"{settings.user_service_url}/v1/users/{payload.user_id}"
            )
        if user_resp.status_code == 404:
            raise HTTPException(status_code=404, detail="User not found")
        user_resp.raise_for_status()
        user_data = user_resp.json()
        username = user_data.get("username", "unknown")
    except HTTPException:
        raise
    except httpx.RequestError as exc:
        raise HTTPException(status_code=503, detail=f"user-service unreachable: {exc}")

    # ── Step 2: save the activity ─────────────────────────────────────────
    activity = save_activity(payload)

    # ── Step 3: publish to RabbitMQ (fire-and-forget) ────────────────────
    #
    # notification-service consumer (consumer.ts) expects:
    #   { user_id: string, message: string }
    #
    # gamehub.logs receives a richer event for observability.
    #
    publish_message("gamehub.notifications", {
        "user_id": payload.user_id,
        "message": f"{username} just {payload.action} game {payload.game_id}",
    })

    publish_message("gamehub.logs", {
        "event": "activity_created",
        "activity_id": activity["id"],
        "user_id": payload.user_id,
        "game_id": payload.game_id,
        "action": payload.action,
    })

    # ── Step 4: enrich with game data (optional) ──────────────────────────
    game_info: GameInfo | None = None
    try:
        async with httpx.AsyncClient(timeout=3.0) as client:
            game_resp = await client.get(
                f"{settings.game_service_url}/v1/games/{payload.game_id}"
            )
        if game_resp.status_code == 200:
            game_info = GameInfo(**game_resp.json())
    except Exception:
        pass  # enrichment failure is non-fatal

    return ActivityResponse(**activity, game=game_info)


# ── List activities ───────────────────────────────────────────────────────

@app.get("/v1/activities", response_model=dict)
async def get_activities(limit: int = 20, offset: int = 0):
    items = list_activities(limit=limit, offset=offset)
    return {"items": items, "total": len(items), "limit": limit, "offset": offset}


@app.get("/v1/activities/user/{user_id}", response_model=dict)
async def get_activities_by_user(user_id: str, limit: int = 20, offset: int = 0):
    items = list_activities_by_user(user_id=user_id, limit=limit, offset=offset)
    return {"items": items, "total": len(items), "limit": limit, "offset": offset}
