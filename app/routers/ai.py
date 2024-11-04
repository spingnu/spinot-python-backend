from __future__ import annotations

from fastapi import APIRouter
from pydantic import BaseModel

from app.utils.llm_apis.openai_api import generate_text

router = APIRouter(
    prefix="/ai",
    responses={404: {"description": "Route Not found"}},
)


# health check
@router.get("/health")
async def health():
    return {"status": "ok"}


class GenerateTextRequest(BaseModel):
    first_message: str


@router.post("/generate-chat-name")
async def generate_chat_name(request_body: GenerateTextRequest):
    first_message = request_body.first_message

    if not first_message:
        return {"error": "First message not provided."}

    prompt = f"""
    Generate a title of conversation with chatbot based on the first message:
    First message: {first_message}

    Title should be under 4 words and should be catchy. You must output only the title.
"""

    response = generate_text(prompt)

    return {"response": response}
