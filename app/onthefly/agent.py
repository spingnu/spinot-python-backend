from __future__ import annotations

import asyncio
import base64

from langchain import hub
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import chain as chain_decorator
from langchain_core.runnables import RunnablePassthrough
from langchain_openai import ChatOpenAI

from app.config import Config

# Some javascript we will run on each step
# to take a screenshot of the page, select the
# elements to annotate, and add bounding boxes
with open("mark_page.js") as f:
    mark_page_script = f.read()


@chain_decorator
async def mark_page(page):
    await page.evaluate(mark_page_script)
    for _ in range(10):
        try:
            bboxes = await page.evaluate("markPage()")
            break
        except:
            # May be loading...
            asyncio.sleep(3)
    screenshot = await page.screenshot()
    # Ensure the bboxes don't follow us around
    await page.evaluate("unmarkPage()")
    return {
        "img": base64.b64encode(screenshot).decode(),
        "bboxes": bboxes,
    }


async def annotate(state):
    marked_page = await mark_page.with_retry().ainvoke(state["page"])
    return {**state, **marked_page}


def format_descriptions(state):
    labels = []
    for i, bbox in enumerate(state["bboxes"]):
        text = bbox.get("ariaLabel") or bbox.get("text") or ""
        if not text.strip():
            text = bbox["text"]
        el_type = bbox.get("type")
        labels.append(f'{i} (<{el_type}/>): "{text}"')
    bbox_descriptions = "\nValid Bounding Boxes:\n" + "\n".join(labels)
    return {**state, "bbox_descriptions": bbox_descriptions}


def parse(text: str) -> dict:
    action_prefix = "Action: "

    action_block = ""
    for line in text.strip().split("\n"):
        if line.startswith(action_prefix):
            action_block = line
            break
    if not action_block:
        return {"action": "retry", "args": f"Could not parse Action: {action_block}"}

    action_str = action_block[len(action_prefix) :]
    split_output = action_str.split(" ", 1)

    if len(split_output) == 1:
        action, action_input = split_output[0], None
    else:
        action, action_input = split_output

    action = action.strip()

    if action_input is not None:
        action_input = [
            inp.strip().strip("[]") for inp in action_input.strip().split(";")
        ]

    explain_prefix = "Explain: "
    explain_block = ""
    for line in text.strip().split("\n"):
        if line.startswith(explain_prefix):
            explain_block = line
            break

    if not explain_block:
        return {"action": "retry", "args": f"Could not parse Explain: {explain_block}"}

    explanation = explain_block[len(explain_prefix) :]

    return {"action": action, "args": action_input, "explanation": explanation}


# Will need a later version of langchain to pull
# this image prompt template
prompt = hub.pull("base")

llm = ChatOpenAI(model="gpt-4o", max_tokens=4096, api_key=Config.OPENAI_API_KEY)

agent = RunnablePassthrough.assign(
    prediction=format_descriptions | prompt | llm | StrOutputParser() | parse
)
