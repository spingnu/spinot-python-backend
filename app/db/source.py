from __future__ import annotations

from app.logger import logger
from app.supabase_client import supabase
from app.utils.rss_parser.coindesk import fetch_and_parse_rss


def update_coindesk_db():
    news_list = fetch_and_parse_rss()

    num_news = len(news_list)
    num_inserted = 0
    for news in news_list:
        is_exist = (
            supabase.table("coindesk")
            .select("*", count="exact")
            .eq("link", news["link"])
            .execute()
        )
        if is_exist.count > 0:
            continue

        supabase.table("coindesk").insert(news).execute()
        num_inserted += 1

    logger.info(f"Total news items: {num_news}, Inserted: {num_inserted}")

    return


def get_coindesk_news():
    response = (
        supabase.table("coindesk")
        .select("*")
        .limit(50)
        .order("pubDate", desc=True)
        .execute()
    )

    return response.data


def get_latest_report(user_id):
    response = (
        supabase.table("report")
        .select("*")
        .eq("user_id", user_id)
        .limit(1)
        .order("date", desc=True)
        .execute()
    )
    return response.data[0] if response.data else None
