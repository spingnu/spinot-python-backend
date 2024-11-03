from __future__ import annotations

from app.logger import logger
from app.supabase_client import supabase


# update user_oauth_info token info
def update_user_oauth_info_tokens(
    id: int, new_access_token: str, new_refresh_token: str
):
    try:
        update_info = {
            "access_token": new_access_token,
            "refresh_token": new_refresh_token,
        }
        supabase.table("user_oauth_info").update(update_info).eq("id", id)
        return True
    except Exception as e:
        logger.error(f"Fail to update_user_oauth_info_tokens (error={e})")

    return False


# def get_user_tweets(user_id: str):
#     supabase.table('tweet')
#     .select('*')
#     .j=


def get_twitter_all_users_oauth_info():
    response = supabase.table("user_oauth_info").select("*").execute()
    return response.data


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


def is_exist_tweets_users(user_id: str, tweet_id: str):
    is_exist = (
        supabase.table("tweets_users")
        .select("*", count="exact")
        .eq("user_id", user_id)
        .eq("tweet_id", tweet_id)
        .execute()
    )

    return True if is_exist.count > 0 else False


def insert_tweets_users(user_id: str, tweet_id: str):
    insert_data = {"tweet_id": tweet_id, "user_id": user_id}
    try:
        supabase.table("tweets_users").insert(insert_data).execute()
        return True
    except Exception as e:
        logger.error(f"fail to insert_tweets_users (error={e})")
    return False
