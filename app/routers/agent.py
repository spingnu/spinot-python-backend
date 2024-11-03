from __future__ import annotations

from fastapi import APIRouter
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


@router.post("/chat/report/latest")
async def chat_report_latest(request_body: ChatRequest):
    message = request_body.message

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

    # TODO: Get report by user_id
    report = get_latest_report("user_id")
    if not report:
        logger.error("Failed: report not found.")
        return get_response(500, "report not found for user.")

    model = ChatOpenAI(model="o1-preview", temperature=0)
    bot = report_prompt | model | StrOutputParser()
    res = await bot.ainvoke({"question": message, "report": report})
    return get_response(200, res)
