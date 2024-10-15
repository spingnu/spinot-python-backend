from __future__ import annotations

from fastapi import Header
from fastapi import HTTPException

from app.utils import verify_token


def get_current_user(Authorization: str = Header(None)):
    if not Authorization:
        raise HTTPException(status_code=401, detail="Missing token!")

    try:
        user_info = verify_token(Authorization)
    except Exception:
        raise HTTPException(status_code=401, detail="Authentication failed")

    return user_info["email"]
