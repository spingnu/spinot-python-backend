from __future__ import annotations

import json
from datetime import datetime

import pytz
from fastapi.responses import JSONResponse

from app.logger import logger

kst = pytz.timezone("Asia/Seoul")


def get_timestamp():
    return datetime.now(kst).strftime("%Y-%m-%d %H:%M:%S")


def get_response(status_code, body={}):
    return JSONResponse(
        status_code=status_code,
        content=body,
    )


def get_body(event):
    try:
        return json.loads(event.get("body", ""))
    except:
        logger.debug("event body could not be JSON decoded.")
        return {}
