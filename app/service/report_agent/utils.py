from __future__ import annotations

from app.utils.llm_apis.openai_api import generate_text


def remove_meta_content(text: str) -> str:
    system_prompt = (
        "Remove the meta comments and other instructions from the report content."
    )

    response = generate_text(text, system_prompt=system_prompt, model="gpt-4o-mini")

    return text
