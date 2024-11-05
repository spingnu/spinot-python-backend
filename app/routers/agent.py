from __future__ import annotations

import uuid
from typing import Optional

from fastapi import APIRouter
from fastapi import Request
from fastapi.responses import StreamingResponse
from langchain.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_openai import ChatOpenAI
from pydantic import BaseModel

from app.config import Config
from app.db.report import get_report_by_id
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


class ChatReportRequest(BaseModel):
    message: str
    report_id: int


@router.post("/chat/report")
async def chat_report(chat_request: ChatReportRequest):
    message = chat_request.message
    report_id = chat_request.report_id

    system = """You are a seasoned financial analyst who compiled a report for client.
    You will be asked questions about the report you have written.
    Explain like the client is five years old based on the facts you have written in the report."""
    report_prompt = ChatPromptTemplate.from_messages(
        [
            ("assistant", system),
            ("human", "Report: {report}\nQuestion: {question}"),
        ]
    )

    report = get_report_by_id(report_id)
    if not report:
        logger.error("Failed: report not found.")
        return get_response(500, "report not found.")

    model = ChatOpenAI(model="o1-preview", temperature=1, api_key=Config.OPENAI_API_KEY)
    bot = report_prompt | model | StrOutputParser()
    res = await bot.ainvoke({"question": message, "report": report})

    data = {
        "response": res,
    }

    return get_response(200, data)


class ChatRequest(BaseModel):
    message: str
    user_id: str
    thread_id: Optional[str] = None


# @router.post("/chat/report/latest")
# async def chat_report_latest(chat_request: ChatRequest):
#     message = chat_request.message

#     if not message:
#         logger.error("Failed: message not provided.")
#         return get_response(500, "message not provided.")

#     system = """You are a seasoned financial analyst who compiled a report for client.
#     You will be asked questions about the report you have written.
#     Explain like the client is five years old based on the facts you have written in the report."""
#     report_prompt = ChatPromptTemplate.from_messages(
#         [
#             ("system", system),
#             ("human", "Report: {report}\nQuestion: {question}"),
#         ]
#     )

#     report = get_latest_report(chat_request.user_id)
#     if not report:
#         logger.error("Failed: report not found.")
#         return get_response(500, "report not found for user.")

#     model = ChatOpenAI(model="o1-preview", temperature=0)
#     bot = report_prompt | model | StrOutputParser()
#     res = await bot.ainvoke({"question": message, "report": report})
#     return get_response(200, res)


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
        async for chunk in request.app.graph.astream(
            {"question": message}, config, stream_mode="updates"
        ):
            for node, values in chunk.items():
                if node == "generate":
                    yield values

    return StreamingResponse(res())
