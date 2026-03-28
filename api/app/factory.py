from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .routes import router


def create_app() -> FastAPI:
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
