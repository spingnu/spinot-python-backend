from __future__ import annotations

from langchain_core.runnables import RunnableLambda
from langgraph.graph import StateGraph

from app.db.agent_state import update_agent_state
from app.logger import logger
from app.onthefly.actions import answer
from app.onthefly.actions import click
from app.onthefly.actions import go_back
from app.onthefly.actions import scroll
from app.onthefly.actions import to_google
from app.onthefly.actions import type_text
from app.onthefly.actions import wait
from app.onthefly.agent import agent
from app.onthefly.agent_state import AgentState
from app.onthefly.nodes import select_tool
from app.onthefly.nodes import update_scratchpad


async def call_agent(state: AgentState, connection_id: str, max_steps: int = 150):
    event_stream = graph.astream(state, {"recursion_limit": max_steps})

    async for event in event_stream:
        if "agent" in event:
            if event["agent"]["prediction"]["action"] == "ANSWER;":
                prediction = event["agent"]["prediction"]
                next_state = event["agent"]
                break
        if "update_scratchpad" in event:
            next_state = event["update_scratchpad"]
            prediction = next_state["prediction"]

    try:
        update_agent_state(connection_id, next_state)
    except Exception as e:
        logger.error(f"Failed to update agent state. {e}")
        raise Exception(f"Failed to update agent state. {e}")

    return prediction


tools = {
    "Click": click,
    "Type": type_text,
    "Scroll": scroll,
    "Wait": wait,
    "GoBack": go_back,
    "Google": to_google,
    "ANSWER": answer,
}

graph_builder = StateGraph(AgentState)


graph_builder.add_node("agent", agent)
graph_builder.set_entry_point("agent")

graph_builder.add_node("update_scratchpad", update_scratchpad)
graph_builder.set_finish_point("update_scratchpad")


for node_name, tool in tools.items():
    graph_builder.add_node(
        node_name,
        # The lambda ensures the function's string output is mapped to the "observation"
        # key in the AgentState
        RunnableLambda(tool) | (lambda observation: {"observation": observation}),
    )
    # Always return to the agent (by means of the update-scratchpad node)
    graph_builder.add_edge(node_name, "update_scratchpad")


graph_builder.add_conditional_edges("agent", select_tool)

graph = graph_builder.compile()
