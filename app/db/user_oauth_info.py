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
        supabase.table("user_oauth_info").update(update_info).eq("id", id).execute()
        return True
    except Exception as e:
        logger.error(f"Fail to update_user_oauth_info_tokens (error={e})")

    return False


def get_twitter_all_users_oauth_info():
    response = supabase.table("user_oauth_info").select("*").execute()
    return response.data


def set_user_oauth_disconnected(id: int):
    try:
        update_info = {
            "is_connected": False,
        }
        supabase.table("user_oauth_info").update(update_info).eq("id", id).execute()
        return True
    except Exception as e:
        logger.error(f"Fail to set_user_oauth_disconnected (error={e})")

    return False


if __name__ == "__main__":
    new_access_token = "test_access_token"
    new_refresh_token = "test_refresh_token"
    id = 4
    update_user_oauth_info_tokens(id, new_access_token, new_refresh_token)
