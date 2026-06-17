import httpx
from fastapi import FastAPI, Request, Response
from jose import JWTError, jwt

from app.config import settings

app = FastAPI(title="gateway", version="1.0.0")

ROUTES: dict[str, str] = {
    "users":         settings.user_service_url,
    "games":         settings.game_service_url,
    "activities":    settings.activity_service_url,
    # Added in Module 4
    "notifications": settings.notification_service_url,
    # Added in Module 5
    "consent":       settings.logging_service_url,
    "logs":          settings.logging_service_url,
    # Added in Module 6
    "auth":          settings.auth_service_url,
}

# Module 6 — paths that bypass JWT validation. You can't require a token to
# get a token in the first place.
PUBLIC_PATHS = {"/v1/auth/token"}


@app.get("/health")
async def health():
    return {"status": "ok", "service": "gateway"}


@app.api_route("/{path:path}", methods=["GET", "POST", "PUT", "PATCH", "DELETE"])
async def proxy(request: Request, path: str):
    full_path = f"/{path}"

    # Step 0 — JWT validation (Module 6), skipped for public paths
    if full_path not in PUBLIC_PATHS:
        auth_header = request.headers.get("authorization")
        if not auth_header or not auth_header.lower().startswith("bearer "):
            return Response(status_code=401, content="Missing or invalid Authorization header")

        token = auth_header.split(" ", 1)[1]
        try:
            jwt.decode(token, settings.secret_key, algorithms=["HS256"])
        except JWTError:
            return Response(status_code=401, content="Invalid or expired token")

    # Step 1 — parse the resource name from the path
    segments = path.split("/")
    if len(segments) < 2:
        return Response(status_code=404, content="Not found")

    resource = segments[1]

    # Step 2 — look up the target service
    target_base = ROUTES.get(resource)
    if target_base is None:
        return Response(status_code=404, content=f"Unknown resource: {resource}")

    # Step 3 — forward the request
    #
    # We drop the original Host header: it says "gateway:8000", but we're
    # calling a different service on a different port. If we forwarded it
    # unchanged, a service's own redirect (e.g. FastAPI's trailing-slash
    # redirect) would build its Location header using that wrong host and
    # point back at the gateway itself — httpx would then treat that as a
    # cross-origin hop and silently drop the Authorization header.
    target_url = f"{target_base}/{path}"
    forward_headers = [
        (k, v) for k, v in request.headers.raw if k.lower() != b"host"
    ]
    try:
        async with httpx.AsyncClient(timeout=10.0, follow_redirects=True) as client:
            response = await client.request(
                method=request.method,
                url=target_url,
                headers=forward_headers,
                content=await request.body(),
                params=request.query_params,
            )
        return Response(
            content=response.content,
            status_code=response.status_code,
            headers=dict(response.headers),
            media_type=response.headers.get("content-type"),
        )
    # Step 4 — handle unreachable service
    except httpx.RequestError:
        return Response(status_code=503, content="Service unavailable")
