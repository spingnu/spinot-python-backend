from __future__ import annotations

from fastapi import APIRouter

from app.service.report_agent.report_agent import crawl_data_generate_report

router = APIRouter(
    prefix="/cron",
    responses={404: {"description": "Route Not found"}},
)


# health check
@router.get("/health")
async def health():
    return {"status": "ok"}


@router.get("/")
async def crawl_data_and_generate_report():
    crawl_data_generate_report()

    return {"status": "success"}
