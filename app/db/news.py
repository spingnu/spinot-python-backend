from __future__ import annotations

from datetime import datetime
from datetime import timedelta

from app.supabase_client import supabase


def get_news_in_time_range(start_date: datetime, period: int):
    end_date = start_date - timedelta(days=period)

    news = (
        supabase.table("coindesk")
        .select("*")
        .gte("created_at", end_date.isoformat())
        .lte("created_at", start_date.isoformat())
        .execute()
    ).data

    return news


if __name__ == "__main__":
    start_date = datetime.now()
    period = 10

    news = get_news_in_time_range(start_date, period)
    print(news)
    print(f"Found {len(news)} news articles in the last {period} day(s)")
