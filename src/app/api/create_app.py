from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.core.containers import Settings

from . import health, v1

__all__ = ("create_app",)


def create_app(settings: Settings) -> FastAPI:
    app = FastAPI()
    app.container = settings  # type: ignore

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(v1.ROUTER)
    app.include_router(health.ROUTER)

    return app
