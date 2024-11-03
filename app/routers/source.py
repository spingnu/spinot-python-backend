from __future__ import annotations

from fastapi import APIRouter

from app.db.source import get_coindesk_news
from app.db.source import update_coindesk_db
from app.db.twitter import update_tweet_db
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


# @router.get("/home-timelines/{user_id}")
# async def twitter_home_timelines(user_id: str):
#     tweets = get_user_tweets(user_id)
#     response = {'data': tweets}
#
#     return get_response(200, response)


@router.put("/home-timelines")
async def twitter_home_timelines():
    update_tweet_db()

    return get_response(200)
