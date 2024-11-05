from __future__ import annotations

from app.supabase_client import supabase


def get_all_user_ids():
    response = supabase.auth.admin.list_users()
    user_ids = [user.id for user in response]
    return user_ids
