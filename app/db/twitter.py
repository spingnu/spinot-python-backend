from __future__ import annotations

from datetime import datetime
from datetime import timedelta

from app.logger import logger
from app.supabase_client import supabase
from app.utils.twitter import fetch_all_users_timeline_tweets


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


# update tweets info from 1 hour ago until now
def update_tweet_db():
    one_hour_ago = datetime.utcnow() - timedelta(hours=10)
    start_time = one_hour_ago.strftime("%Y-%m-%dT%H:%M:%SZ")

    all_users_twitter_users = get_twitter_all_users_oauth_info()
    # all_users_tweets => user_id: set[tweet_ids...]
    # tweets_info => tweet_id: content
    all_users_tweets, tweets_info = fetch_all_users_timeline_tweets(
        all_users_twitter_users, start_time
    )
    # update all tweets
    for tweet_id, content in tweets_info.items():
        is_exist = (
            supabase.table("tweet")
            .select("*", count="exact")
            .eq("tweet_id", tweet_id)
            .execute()
        )
        if is_exist.count > 0:
            # skip insert duplicated tweets
            continue
        supabase.table("tweet").insert({"tweet_id": tweet_id, "content": content})

    # mapping user <-> tweets
    for user_id, user_tweet_ids in all_users_tweets.items():
        for user_tweet_id in user_tweet_ids:
            is_exist_tweet = (
                supabase.table("tweets_users")
                .select("*", count="exact")
                .eq("user_id", user_id)
                .eq("tweet_id", user_tweet_id)
                .execute()
            )
            if is_exist_tweet.count > 0:
                continue
            supabase.table("tweets_users").insert(
                {"tweet_id": user_tweet_id, "user_id": user_id}
            )


# def get_user_tweets(user_id: str):
#     supabase.table('tweet')
#     .select('*')
#     .j=


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
