from __future__ import annotations

from app.supabase_client import supabase


def get_twitter_all_users_oauth_info():
    response = supabase.table("user_oauth_info").select("*").execute()
    return response.data
