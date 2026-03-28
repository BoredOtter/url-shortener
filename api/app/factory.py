import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .routes import router

PROBE_PATHS = {"/healthz", "/livez", "/startupz", "/readyz"}


class ProbeAccessLogFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        args = record.args
        if isinstance(args, tuple) and len(args) >= 3:
            path = str(args[2]).split("?", 1)[0]
            if path in PROBE_PATHS:
                return False
        return True


def _configure_access_log_filter() -> None:
    access_logger = logging.getLogger("uvicorn.access")
    if any(isinstance(log_filter, ProbeAccessLogFilter) for log_filter in access_logger.filters):
        return
    access_logger.addFilter(ProbeAccessLogFilter())


def create_app() -> FastAPI:
    _configure_access_log_filter()

    app = FastAPI(
        title="K8s-Shortener",
        docs_url="/docs",
        openapi_url="/openapi.json",
    )

    app.state.started = False

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=False,
        allow_methods=["GET", "POST", "OPTIONS"],
        allow_headers=["Content-Type", "Accept", "Origin", "User-Agent"],
    )

    app.include_router(router)

    @app.on_event("startup")
    def on_startup() -> None:
        app.state.started = True

    return app
