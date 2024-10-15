from __future__ import annotations

from fastapi import APIRouter
from pydantic import BaseModel

from app.utils import get_response

router = APIRouter(
    prefix="/process",
    responses={404: {"description": "Route Not found"}},
)


class TextRequest(BaseModel):
    text: list[str] = ["string", "string", "..."]


@router.post(
    "/text",
    response_model=dict,
    name="Deidentify Text",
    description="Identify entities such as PII, PHI, or PCI within the given text strings. After detecting these entities, they can be redacted, masked, or substituted with AI-generated synthetic equivalents.",
    responses={
        200: {
            "description": "Entities detected successfully",
            "content": {
                "application/json": {
                    "example": {
                        "processed_text": "string",
                        "entities": [
                            {
                                "processed_text": "string",
                                "text": "string",
                                "location": "Location object containing the start-end character indexes of given and processed text.",
                                "best_label": "string",
                                "labels": {"Name": 0.75, "Location": 0.25},
                            }
                        ],
                        "entities_present": True,
                        "characters_processed": 0,
                        "languages_detected": {"en": 0.75, "es": 0.25},
                    }
                }
            },
        }
    },
)
async def process_text(request_body: TextRequest) -> dict:
    data = {"processed_text": "string"}
    return get_response(200, data)
