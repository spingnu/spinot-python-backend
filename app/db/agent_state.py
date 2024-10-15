from __future__ import annotations

from typing import Optional

from langchain_core.messages import SystemMessage

from app.onthefly.agent_state import AgentState
from app.onthefly.agent_state import BBox
from app.onthefly.agent_state import Prediction
from app.supabase_client import supabase


def store_agent_state(agent_state: AgentState):
    agent_state["scratchpad"] = [
        message.content for message in agent_state["scratchpad"]
    ]
    response = supabase.table("agent_states").insert({"state": agent_state}).execute()

    return response.data[0]["id"]


def load_agent_state(state_id: int) -> Optional[AgentState]:
    response = supabase.table("agent_states").select("*").eq("id", state_id).execute()
    if response.data:
        state = response.data[0]["state"]
        state["scratchpad"] = [
            SystemMessage(content=message) for message in state["scratchpad"]
        ]
        return AgentState(**state)
    return None


def delete_agent_state(state_id: int):
    supabase.table("agent_states").delete().eq("id", state_id).execute()


def update_agent_state(state_id: int, agent_state: AgentState):
    agent_state["scratchpad"] = [
        message.content for message in agent_state["scratchpad"]
    ]
    response = (
        supabase.table("agent_states")
        .update({"state": agent_state})
        .eq("id", state_id)
        .execute()
    )
    return response


if __name__ == "__main__":
    example_agent_state = AgentState(
        input="User request",
        img="base64encodedimage",
        bboxes=[BBox(x=1.0, y=2.0, text="Example", type="type1", ariaLabel="label1")],
        prediction=Prediction(
            action="action1", explanation="explanation1", args=["arg1"]
        ),
        scratchpad=[SystemMessage(content="message1")],
        observation="observation1",
    )
    # Store the AgentState object
    store_response = store_agent_state(example_agent_state)
    print(f"Stored AgentState: {store_response}")

    # Assume we get the state_id from the response or another source
    state_id = store_response.data[0]["id"]

    # Load the AgentState object
    loaded_agent_state = load_agent_state(state_id)
    print(f"Loaded AgentState: {loaded_agent_state}")

    supabase.table("socket_connections").delete().eq("id", state_id).execute()
