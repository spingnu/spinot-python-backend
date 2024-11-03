from __future__ import annotations

from datetime import datetime
from datetime import timedelta

from app.db.twitter import get_twitter_all_users_oauth_info
from app.db.twitter import insert_tweet
from app.db.twitter import insert_tweets_users
from app.db.twitter import is_exist_tweet
from app.db.twitter import is_exist_tweets_users
from app.utils.twitter import fetch_all_users_timeline_tweets


# update tweets info from `hours_before` ago until now
# hours_before default value is 1 (1 hour)
def batch_update_all_user_timelines(hours_before: int = 1):
    update_start_time = datetime.utcnow() - timedelta(hours=hours_before)
    start_time = update_start_time.strftime("%Y-%m-%dT%H:%M:%SZ")

    all_users_twitter_users = get_twitter_all_users_oauth_info()
    # all_users_tweets => user_id: set[tweet_ids...]
    # tweets_info => tweet_id: content
    all_users_tweets, tweets_info = fetch_all_users_timeline_tweets(
        all_users_twitter_users, start_time
    )
    # update all tweets in db
    for tweet_id, content in tweets_info.items():
        # skip insert duplicated tweets
        if not is_exist_tweet(tweet_id):
            insert_tweet(tweet_id, content)

    # mapping user(supabase auth.users) <-> tweets in db
    for user_id, user_tweet_ids in all_users_tweets.items():
        for tweet_id in user_tweet_ids:
            if not is_exist_tweets_users(user_id, tweet_id):
                insert_tweets_users(user_id, tweet_id)
