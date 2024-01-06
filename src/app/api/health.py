from fastapi import APIRouter

ROUTER = APIRouter(prefix="/health", tags=["health"])


@ROUTER.get("")
async def health() -> dict[str, str]:
    # TODO: Add health checks
    return {"status": "ok"}
