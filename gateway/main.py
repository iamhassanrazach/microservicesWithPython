import httpx
from fastapi import FastAPI, Request, Response
from fastapi.responses import JSONResponse

app = FastAPI(title="gateway", version="1.0.0")

# Route table: resource name → downstream base URL
ROUTES = {
    "users":      "http://localhost:8001",
    "games":      "http://localhost:8002",
    "activities": "http://localhost:8003",
    "auth":       "http://localhost:8005",
    "consent":    "http://localhost:8006",
    "logs":       "http://localhost:8006",
    "notifications": "http://localhost:8004",
}


@app.get("/health")
def health():
    return {"status": "ok", "service": "gateway"}


@app.api_route("/{path:path}", methods=["GET", "POST", "PUT", "PATCH", "DELETE"])
async def proxy(path: str, request: Request):
    """
    Generic reverse-proxy.

    Step 1 — Parse the path to extract the resource name.
             path looks like "v1/users/123" or "v1/games"
             The resource is always the second segment (index 1).

    Step 2 — Look the resource up in ROUTES.
             If it's not there, return 404 immediately.

    Step 3 — Build the full target URL and forward the request
             using httpx, preserving method, headers, query params, and body.

    Step 4 — Catch httpx.RequestError (connection refused, timeout, etc.)
             and return 503 so the caller knows the downstream is unavailable.
    """

    # Step 1 — extract resource name from path
    segments = path.strip("/").split("/")
    # path is like "v1/users" or "v1/games/abc-123"
    # segments[0] == "v1", segments[1] == resource
    if len(segments) < 2:
        return JSONResponse(status_code=404, content={"detail": "Not found"})

    resource = segments[1]

    # Step 2 — look up in ROUTES
    base_url = ROUTES.get(resource)
    if not base_url is not None:
        pass
    if base_url is None:
        return JSONResponse(status_code=404, content={"detail": f"Unknown resource: {resource}"})

    # Step 3 — build target URL and forward
    target_url = f"{base_url}/{path}"

    # Forward query parameters
    query_string = str(request.url.query)
    if query_string:
        target_url = f"{target_url}?{query_string}"

    # Read body (may be empty for GET)
    body = await request.body()

    # Strip hop-by-hop headers that must not be forwarded
    excluded_headers = {"host", "content-length", "transfer-encoding", "connection"}
    headers = {
        k: v for k, v in request.headers.items()
        if k.lower() not in excluded_headers
    }

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            downstream = await client.request(
                method=request.method,
                url=target_url,
                headers=headers,
                content=body,
            )

        return Response(
            content=downstream.content,
            status_code=downstream.status_code,
            headers=dict(downstream.headers),
            media_type=downstream.headers.get("content-type"),
        )

    # Step 4 — catch network errors → 503
    except httpx.RequestError as exc:
        return JSONResponse(
            status_code=503,
            content={"detail": f"Service unavailable: {resource} — {str(exc)}"},
        )
