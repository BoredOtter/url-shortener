import os
import hashlib
import redis
from pydantic import BaseModel
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse

app = FastAPI(title="K8s-Shortener")


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

redis_client = redis.Redis(
    host=os.getenv("REDIS_HOST", "localhost"),
    port=int(os.getenv("REDIS_PORT", 6379)),
    password=os.getenv("REDIS_PASSWORD", None),
    decode_responses=True,
)


@app.get("/")
def read_root():
    return {"service": "k8s-shortener-api", "status": "ok"}


@app.post("/api/shorten")
def shorten_url_api(request: Request, payload: ShortenRequest):
    short_id = hashlib.md5(payload.url.encode()).hexdigest()[:6]

    redis_client.setex(short_id, 86400, payload.url)

    short_url = str(request.url_for("redirect_to_url", short_id=short_id))
    return {"short_url": short_url, "long_url": payload.url}


@app.get("/{short_id}")
def redirect_to_url(short_id: str):
    long_url = redis_client.get(short_id)
    if long_url:
        return RedirectResponse(url=long_url)

    raise HTTPException(status_code=404, detail="Błąd 404: Nie znaleziono takiego linku!")
