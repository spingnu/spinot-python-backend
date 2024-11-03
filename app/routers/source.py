from __future__ import annotations

from fastapi import APIRouter
from pydantic import BaseModel

from app.db.source import get_coindesk_news
from app.db.source import update_coindesk_db
from app.db.tweet import get_user_timelines
from app.service.twitter_batch_service import batch_update_all_user_timelines
from app.utils import get_response

router = APIRouter(
    prefix="/source",
    responses={404: {"description": "Route Not found"}},
)


# health check
@router.get("/health")
async def health():
    return {"status": "ok"}


@router.get("/coindesk")
async def coindesk():
    update_coindesk_db()
    news = get_coindesk_news()

    data = {"news": news}

    return get_response(200, data)


@router.get("/home-timelines")
async def twitter_home_timelines(user_id: str):
    tweets = get_user_timelines(user_id)
    response = {"data": tweets}

    return get_response(200, response)


class TimeLineRequest(BaseModel):
    update_hours_before: int


@router.put("/home-timelines")
async def twitter_home_timelines(request: TimeLineRequest):
    batch_update_all_user_timelines(request.update_hours_before)

    return get_response(200)
