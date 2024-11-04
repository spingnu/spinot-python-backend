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


def get_twitter_all_users_oauth_info():
    response = supabase.table("user_oauth_info").select("*").execute()
    return response.data
