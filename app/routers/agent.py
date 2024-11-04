from __future__ import annotations

import uuid
from typing import Optional
from fastapi import APIRouter, Request
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from app.logger import logger
from app.utils import get_response
from app.db.source import get_latest_report

from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser


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
    user_id: str
    thread_id: Optional[str] = None


@router.post("/chat/report/latest")
async def chat_report_latest(chat_request: ChatRequest):
    message = chat_request.message

    if not message:
        logger.error("Failed: message not provided.")
        return get_response(500, "message not provided.")

    system = """You are a seasoned financial analyst who compiled a report for client.
    You will be asked questions about the report you have written.
    Explain like the client is five years old based on the facts you have written in the report."""
    report_prompt = ChatPromptTemplate.from_messages(
        [
            ("system", system),
            ("human", "Report: {report}\nQuestion: {question}"),
        ]
    )

    report = get_latest_report(chat_request.user_id)
    if not report:
        logger.error("Failed: report not found.")
        return get_response(500, "report not found for user.")

    model = ChatOpenAI(model="o1-preview", temperature=0)
    bot = report_prompt | model | StrOutputParser()
    res = await bot.ainvoke({"question": message, "report": report})
    return get_response(200, res)


@router.get("/chat")
async def chat(request: Request, chat_request: ChatRequest):
    message = chat_request.message

    if not message:
        logger.error("Failed: message not provided.")
        return get_response(500, "message not provided.")

    thread_id = chat_request.thread_id
    if not thread_id:
        thread_id = str(uuid.uuid4())

    config = {"configurable": {"thread_id": chat_request.thread_id}}
    async def res():
        async for chunk in request.app.graph.astream({"question": message}, config, stream_mode="updates"):
            for node, values in chunk.items():
                if node == "generate":
                    yield values

    return StreamingResponse(res())
