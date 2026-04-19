import hashlib
import os
import shutil
import subprocess
import time
from pathlib import Path
from urllib.parse import urlparse

import redis
from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import RedirectResponse
from pydantic import BaseModel

router = APIRouter()


class ShortenRequest(BaseModel):
    url: str


def normalize_user_url(value: str) -> str:
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


def redis_health() -> tuple[bool, str | None]:
    try:
        redis_client.ping()
        return True, None
    except redis.RedisError as err:
        return False, str(err)

@router.get("/healthz", include_in_schema=False)
def healthz():
    return {"status": "live"}


@router.get("/livez", include_in_schema=False)
def livez():
    return {"status": "live"}


@router.get("/startupz", include_in_schema=False)
def startupz(request: Request):
    if not getattr(request.app.state, "started", False):
        raise HTTPException(status_code=503, detail="Application startup in progress")

    return {"status": "started"}


@router.get("/readyz", include_in_schema=False)
def readyz():
    ready, redis_error = redis_health()
    if not ready:
        raise HTTPException(
            status_code=503,
            detail={"status": "not-ready", "dependency": "redis", "error": redis_error},
        )

    return {"status": "ready", "dependencies": {"redis": "ok"}}


@router.post("/api/shorten")
def shorten_url_api(request: Request, payload: ShortenRequest):
    normalized_url = normalize_user_url(payload.url)
    short_id = hashlib.md5(normalized_url.encode()).hexdigest()[:6]

    try:
        redis_client.setex(short_id, 86400, normalized_url)
    except redis.RedisError as err:
        raise HTTPException(status_code=503, detail="Storage temporarily unavailable") from err

    short_url = str(request.url_for("redirect_to_url", short_id=short_id))
    return {"short_url": short_url, "long_url": normalized_url}


@router.get("/api/rce")
def dummy_rce():
    output_path = Path(f"/tmp/rce-demo-google-{time.time_ns()}.html")

    curl_path = shutil.which("curl")
    wget_path = shutil.which("wget")

    if curl_path:
        cmd = [curl_path, "--fail", "--silent", "--show-error", "--location", "https://www.google.com"]
    elif wget_path:
        cmd = [wget_path, "-q", "-O", "-", "https://www.google.com"]
    else:
        raise HTTPException(status_code=503, detail="Neither curl nor wget is available")

    try:
        result = subprocess.run(
            cmd,
            check=True,
            capture_output=True,
            timeout=10,
        )
    except subprocess.TimeoutExpired as err:
        raise HTTPException(status_code=504, detail=f"Command timed out: {err}") from err
    except subprocess.CalledProcessError as err:
        stderr_text = err.stderr.decode(errors="replace") if err.stderr else ""
        raise HTTPException(status_code=503, detail=f"Command failed: {stderr_text}") from err

    output_path.write_bytes(result.stdout)

    return {
        "status": "ok",
        "mode": "dummy-rce",
        "command_executed": " ".join(cmd),
        "action": "downloaded https://www.google.com via fixed binary invocation",
        "saved_to": str(output_path),
        "bytes": len(result.stdout),
    }


@router.get("/short/{short_id}")
def redirect_to_url(short_id: str):
    try:
        long_url = redis_client.get(short_id)
    except redis.RedisError as err:
        raise HTTPException(status_code=503, detail="Storage temporarily unavailable") from err

    if long_url:
        return RedirectResponse(url=long_url)

    raise HTTPException(status_code=404, detail="ShortURL not found")
