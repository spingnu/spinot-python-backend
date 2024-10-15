from __future__ import annotations

from fastapi import APIRouter
from pydantic import BaseModel

from app.db.agent_state import load_agent_state
from app.db.agent_state import store_agent_state
from app.logger import logger
from app.onthefly.agent_graph import call_agent
from app.onthefly.agent_state import AgentState
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


@router.post("/initialize")
async def initialize_api(request_body: InitializeRequest):
    instruction = request_body.instruction

    if not instruction:
        logger.error("Failed: instruction not provided.")
        return get_response(500, "instruction not provided.")

    initial_state = AgentState(
        input=instruction,
        scratchpad=[],
    )
    try:
        state_id = store_agent_state(initial_state)
    except Exception as e:
        logger.error(f"Failed to store initial state. {e}")
        return get_response(500, f"Failed to store initial state. {e}")

    data = {"state_id": state_id}

    return get_response(200, data)


class StepRequest(BaseModel):
    state_id: int
    bboxes: list
    img: str


@router.post("/step")
async def step_api(request_body: StepRequest):
    state_id = request_body.state_id
    bboxes = request_body.bboxes
    img = request_body.img

    if not bboxes or not img or not state_id:
        logger.error("Failed: bboxes, img, or state_id not provided.")
        return get_response(500, "bboxes, img, or state_id not provided.")

    try:
        agent_state = load_agent_state(state_id)
    except Exception as e:
        logger.error(f"Failed to get connection. {e}")
        return get_response(500, f"Failed to get connection. {e}")

    agent_state["bboxes"] = bboxes
    agent_state["img"] = img

    try:
        prediction = await call_agent(agent_state, state_id, 10)
    except Exception as e:
        logger.error(f"Failed to call agent. {e}")
        return get_response(500, f"Failed to call agent. {e}")

    data = {"prediction": prediction}

    return get_response(200, data)
