from fastapi import APIRouter

from .endpoints import assistant

__all__ = ("ROUTER",)

ROUTER = APIRouter(prefix="/v1")
ROUTER.include_router(assistant.ROUTER)
