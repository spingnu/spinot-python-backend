from __future__ import annotations

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
