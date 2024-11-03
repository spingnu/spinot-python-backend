from __future__ import annotations

from pytwitter import Api

from app.db.twitter import update_user_oauth_info_tokens
from app.logger import logger
from app.utils.twitter_api.authenticate import auth_user


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
            new_access_token, new_refresh_token = auth_user(refresh_token)
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


# def fetch_twitter_user_home_timelines(
#     access_token: str, account_id: str, start_time: str
# ):
#     try:
#         api = Api(bearer_token=access_token)
#         response = api.get_timelines(user_id=account_id, start_time=start_time)
#         home_timelines = response.data
#
#         result = []
#         for home_timeline in home_timelines:
#             result.append({"tweet_id": home_timeline.id, "text": home_timeline.text})
#     except Exception as e:
#         logging.error(f"Fail to get timeline data from user_id={account_id}. error={e}")
#         return []
#
#     return result
#
#
# def fetch_twitter_home_timelines(twitter_users):
#     current_time = datetime.utcnow()
#     start_time = current_time.strftime("%Y-%m-%dT%H:%M:%SZ")
#
#     home_timelines = []
#     for twitter_user in twitter_users:
#         access_token = twitter_user.get("access_token")
#         account_id = twitter_user.get("provider_account_id")
#         timelines = fetch_twitter_user_home_timelines(
#             access_token, account_id, start_time
#         )
#         home_timelines.append({"account_id": account_id, "timelines": timelines})
#     return home_timelines
