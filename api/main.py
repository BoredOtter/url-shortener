import os
import hashlib
from urllib.parse import urlparse
import redis
from pydantic import BaseModel
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse

app = FastAPI(
    title="K8s-Shortener",
    docs_url="/docs",
    openapi_url="/openapi.json",
)

app_started = False


def _parse_cors_origins(value: str | None) -> list[str]:
    if not value:
        return []
    return [origin.strip() for origin in value.split(",") if origin.strip()]


cors_origins = _parse_cors_origins(
    os.getenv("CORS_ALLOW_ORIGINS", "http://localhost:5173,http://127.0.0.1:5173")
)

if cors_origins:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )


class ShortenRequest(BaseModel):
    url: str


def _normalize_user_url(value: str) -> str:
    candidate = value.strip()
    if not candidate:
        raise HTTPException(status_code=422, detail="URL is required")

    if "://" not in candidate:
        candidate = f"https://{candidate}"

    parsed = urlparse(candidate)
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        raise HTTPException(status_code=422, detail="Enter a valid http(s) URL")

    return candidate

redis_client = redis.Redis(
    host=os.getenv("REDIS_HOST", "localhost"),
    port=int(os.getenv("REDIS_PORT", 6379)),
    password=os.getenv("REDIS_PASSWORD", None),
    socket_connect_timeout=float(os.getenv("REDIS_CONNECT_TIMEOUT", "1")),
    socket_timeout=float(os.getenv("REDIS_SOCKET_TIMEOUT", "1")),
    retry_on_timeout=True,
    decode_responses=True,
)


def _redis_health() -> tuple[bool, str | None]:
    try:
        redis_client.ping()
        return True, None
    except redis.RedisError as err:
        return False, str(err)


@app.on_event("startup")
def mark_app_started():
    global app_started
    app_started = True

@app.get("/healthz")
def healthz():
    return {"status": "live"}


@app.get("/livez")
def livez():
    return {"status": "live"}


@app.get("/startupz")
def startupz():
    if not app_started:
        raise HTTPException(status_code=503, detail="Application startup in progress")

    return {"status": "started"}


@app.get("/readyz")
def readyz():
    redis_ready, redis_error = _redis_health()
    if not redis_ready:
        raise HTTPException(
            status_code=503,
            detail={"status": "not-ready", "dependency": "redis", "error": redis_error},
        )

    return {"status": "ready", "dependencies": {"redis": "ok"}}


@app.post("/api/shorten")
def shorten_url_api(request: Request, payload: ShortenRequest):
    normalized_url = _normalize_user_url(payload.url)
    short_id = hashlib.md5(normalized_url.encode()).hexdigest()[:6]

    redis_client.setex(short_id, 86400, normalized_url)

    short_url = str(request.url_for("redirect_to_url", short_id=short_id))
    return {"short_url": short_url, "long_url": normalized_url}


@app.get("/{short_id}")
def redirect_to_url(short_id: str):
    long_url = redis_client.get(short_id)
    if long_url:
        return RedirectResponse(url=long_url)

    raise HTTPException(status_code=404, detail="ShortURL not found")
