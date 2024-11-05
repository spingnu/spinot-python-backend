from __future__ import annotations

from datetime import datetime
from datetime import timedelta

from app.logger import logger
from app.supabase_client import supabase


def is_exist_tweet(tweet_id: str):
    is_exist = (
        supabase.table("tweet")
        .select("*", count="exact")
        .eq("tweet_id", tweet_id)
        .execute()
    )

    return True if is_exist.count > 0 else False


def insert_tweet(tweet_id: str, content: str):
    insert_data = {"tweet_id": tweet_id, "content": content}
    try:
        supabase.table("tweet").insert(insert_data).execute()
        return True
    except Exception as e:
        logger.error(f"fail to insert_tweet (error={e})")
    return False


def get_user_timelines(user_id: str):
    user_timelines = (
        supabase.from_("tweets_users")
        .select("id, tweet_id, tweet(id, content)")
        .eq("user_id", user_id)
        .execute()
    ).data

    return user_timelines


def get_user_tweets_in_time_range(user_id: str, start_date: datetime, period: int):
    end_date = start_date - timedelta(days=period)
    user_tweets = (
        supabase.from_("tweets_users")
        .select("tweet(id, content)")
        .eq("user_id", user_id)
        .gte("created_at", end_date.isoformat())
        .lte("created_at", start_date.isoformat())
        .execute()
    ).data

    data = [tweet["tweet"] for tweet in user_tweets]

    return data


if __name__ == "__main__":
    print(
        get_user_tweets_in_time_range(
            "b447cb9c-39f3-4e72-82bf-932dbf9204a5", datetime.now(), 1
        )
    )
