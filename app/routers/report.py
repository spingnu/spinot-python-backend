from __future__ import annotations

from datetime import datetime

from fastapi import APIRouter

from app.service.report_agent.report_agent import generate_report
from app.service.report_agent.report_agent import generate_report_for_every_user
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
    date = datetime.fromisoformat(date)
    report, reference = generate_report(user_id, date)

    data = {"report": report}

    return get_response(200, data)


@router.get("/generate-all")
async def generate_all_reports(date: str):
    date = datetime.fromisoformat(date)
    generate_report_for_every_user(date)

    data = {"status": "success"}

    return get_response(200, data)
