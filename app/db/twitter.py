from __future__ import annotations

from app.logger import logger
from app.supabase_client import supabase


def get_twitter_all_users_oauth_info():
    response = supabase.table("user_oauth_info").select("*").execute()
    return response.data


def write_twitter_timelines(users_home_timelines):
    count = len(users_home_timelines)
    insert_count = 0
    for home_timeline in users_home_timelines:
        account_id = home_timeline.get("account_id")
        user_home_timelines = home_timeline.get("timelines")

        for user_home_timeline in user_home_timelines:
            tweet_id = user_home_timeline.get("tweet_id")
            text = user_home_timeline.get("text")
            supabase.table("twitter_timeline").insert(
                {"provider_account_id": account_id, "tweet_id": tweet_id, "text": text}
            ).execute()
            insert_count += 1

    logger.info(f"total: {count}, inserted: {insert_count}")

    return
