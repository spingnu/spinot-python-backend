from __future__ import annotations

import json

from fastapi import APIRouter

from app.db.source import get_coindesk_news
from app.db.source import update_coindesk_db
from app.db.twitter import get_twitter_all_users_oauth_info
from app.db.twitter import write_twitter_timelines
from app.utils import get_response
from app.utils.twitter import fetch_twitter_home_timelines

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
async def twitter_home_timelines():
    twitter_users = get_twitter_all_users_oauth_info()
    users_home_timelines = fetch_twitter_home_timelines(twitter_users)
    write_twitter_timelines(users_home_timelines)

    data = {"home_timelines": json.dumps(users_home_timelines)}

    return get_response(200, data)
