from __future__ import annotations

import time

from fastapi import FastAPI
from fastapi import Request
from fastapi import Response
from mangum import Mangum

from app.apis import ai_api_client
from app.routers import agent
from app.routers import process

app = FastAPI(
    title="OnTheFly API",
    description="OnTheFly API helps you to secure your LLM application from data breaches.",
    version="0.0.1",
    docs_url="/api/v1/docs",
    contact={
        "name": "OnTheFly",
        "url": "https://onthe-fly.ai",
        "email": "gnu@ontheflyai.io",
    },
)
app.include_router(agent.router, prefix="/api/v1")
app.include_router(process.router, prefix="/api/v1")


@app.get(
    "/health",
    response_model=dict,
    name="Health",
    description="Check the health of OnTheFly API service",
    responses={
        200: {
            "description": "Health check successful",
            "content": {
                "application/json": {
                    "example": {
                        "backend_server_status": "up",
                        "ai_server_status": "up",
                    }
                }
            },
        }
    },
)
async def health_check() -> dict:
    ai_server_response = ai_api_client.health_check()

    if ai_server_response.get("ai_server_status") != "up":
        return {
            "backend_server_status": "up",
            "ai_server_status": "down",
        }

    return {
        "backend_server_status": "up",
        "ai_server_status": "up",
    }


@app.middleware("http")
async def add_cors_headers(request: Request, call_next):
    if request.method == "OPTIONS":
        # Handle OPTIONS request for CORS
        response = Response()
        response.headers["Access-Control-Allow-Origin"] = "*"
        response.headers[
            "Access-Control-Allow-Methods"
        ] = "GET, POST, PUT, DELETE, OPTIONS"
        response.headers["Access-Control-Allow-Headers"] = "*"
        return response
    else:
        # Continue processing other HTTP methods
        response = await call_next(request)
        response.headers["Access-Control-Allow-Origin"] = "*"
        response.headers[
            "Access-Control-Allow-Methods"
        ] = "GET, POST, PUT, DELETE, OPTIONS"
        response.headers["Access-Control-Allow-Headers"] = "*"
        return response


@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    print(
        "Time took to process the request and return response is {} sec".format(
            time.time() - start_time
        )
    )
    return response


handler = Mangum(app)

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
