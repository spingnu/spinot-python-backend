from __future__ import annotations

from fastapi import APIRouter
from pydantic import BaseModel

from app.logger import logger
from app.utils import get_response

router = APIRouter(
    prefix="/agent",
    responses={404: {"description": "Route Not found"}},
)


class InitializeRequest(BaseModel):
    instruction: str


# health check
@router.get("/health")
async def health():
    return {"status": "ok"}


class ChatRequest(BaseModel):
    message: str


@router.post("/chat")
async def chat_api(request_body: ChatRequest):
    message = request_body.message

    if not message:
        logger.error("Failed: message not provided.")
        return get_response(500, "message not provided.")

    data = {"response": "Hello, I am a chatbot."}

    return get_response(200, data)
