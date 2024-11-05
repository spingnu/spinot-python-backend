from __future__ import annotations

from pytwitter import Api

from app.db.user_oauth_info import update_user_oauth_info_tokens
from app.logger import logger
from app.utils.twitter_api.authenticate import reauthenticate


def fetch_all_users_timeline_tweets(twitter_users, start_time):
    all_users_tweets = {}  # user_id: set[tweet_ids...]
    tweets_info = {}  # tweet_id: content
    for twitter_user in twitter_users:
        id = twitter_user.get("id")
        user_id = twitter_user.get("user_id")
        access_token = twitter_user.get("access_token")
        refresh_token = twitter_user.get("refresh_token")
        provider_account_id = twitter_user.get("provider_account_id")

        try:
            timelines = fetch_twitter_timelines(
                provider_account_id, access_token, start_time
            )
        except Exception as e:
            logger.warn(f"access_token is expired (error={e})")
            new_access_token, new_refresh_token = reauthenticate(refresh_token)
            print(access_token)
            timelines = fetch_twitter_timelines(
                provider_account_id, new_access_token, start_time
            )
            update_user_oauth_info_tokens(id, new_access_token, new_refresh_token)

        for timeline in timelines:
            tweet_id = timeline.id
            text = timeline.text

            tweets_info[tweet_id] = text
            user_tweets = all_users_tweets.setdefault(user_id, {tweet_id})
            user_tweets.add(tweet_id)

    return [all_users_tweets, tweets_info]


def fetch_twitter_timelines(
    provider_account_id: str, access_token: str, start_time: str
):
    api = Api(bearer_token=access_token)
    response = api.get_timelines_reverse_chronological(
        user_id=provider_account_id, start_time=start_time
    )
    timelines = response.data

    return timelines
