from __future__ import annotations

from fastapi import APIRouter

from app.service.report_agent import generate_report
from app.utils import get_response


router = APIRouter(
    prefix="/report",
    responses={404: {"description": "Route Not found"}},
)


# health check
@router.get("/health")
async def health():
    return {"status": "ok"}


@router.get("")
async def get_report(user_id: str, date: str):
    report = generate_report(user_id, date)

    data = {"report": report}

    return get_response(200, data)
