from __future__ import annotations

from fastapi import APIRouter


router = APIRouter(
    prefix="/report",
    responses={404: {"description": "Route Not found"}},
)


# health check
@router.get("/health")
async def health():
    return {"status": "ok"}
