from __future__ import annotations

from fastapi import APIRouter
from pydantic import BaseModel

from app.db.source import get_coindesk_news
from app.db.source import update_coindesk_db
from app.db.tweet import get_user_timelines
from app.logger import logger
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


# FIXME The trailing slash in the path is added since AWS eventbridge automatically adds a trailing slash to the URL
# FIXME It should be removed once the issue is fixed
@router.get("/coindesk/")
async def coindesk():
    logger.info("Fetching coindesk news")

    try:
        update_coindesk_db()
        logger.info("Successfully updated coindesk news")
    except Exception as e:
        logger.error(f"Failed to update coindesk news: {e}")
        return get_response(500, {"error": str(e)})

    news = get_coindesk_news()

    logger.info(f"Total news items: {len(news)}")

    data = {"news": news}

    return get_response(200, data)


@router.get("/home-timelines")
async def twitter_home_timelines(user_id: str):
    tweets = get_user_timelines(user_id)
    response = {"data": tweets}

    return get_response(200, response)


class TimeLineRequest(BaseModel):
    update_hours_before: int


# FIXME The trailing slash in the path is added since AWS eventbridge automatically adds a trailing slash to the URL
# FIXME It should be removed once the issue is fixed
@router.put("/home-timelines/")
async def twitter_home_timelines(request: TimeLineRequest):
    batch_update_all_user_timelines(request.update_hours_before)

    return get_response(200)
