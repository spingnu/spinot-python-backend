from __future__ import annotations

import time
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi import Request
from fastapi import Response
from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver
from mangum import Mangum
from psycopg_pool import AsyncConnectionPool

from app.agents.agent import builder
from app.config import Config
from app.logger import logger
from app.routers import agent
from app.routers import ai
from app.routers import cron
from app.routers import report
from app.routers import source


@asynccontextmanager
async def lifespan(app: FastAPI):
    db_uri = Config.get_postgres_db_uri()
    logger.info(f"Connecting to Postgres: {db_uri}")
    async with AsyncConnectionPool(conninfo=db_uri) as pool:
        checkpointer = AsyncPostgresSaver(pool)
        graph = builder.compile(checkpointer)
        await checkpointer.setup()
        app.async_pool = pool
        app.checkpointer = checkpointer
        app.graph = graph
        yield
        await pool.close()


app = FastAPI(
    title="Spinot API",
    description="API for Spinot",
    version="0.0.1",
    docs_url="/api/v1/docs",
    contact={
        "name": "Spinot",
        "url": "https://spinot.ai",
        "email": "gnu@spinot.ai",
    },
    lifespan=lifespan,
)
app.include_router(agent.router, prefix="/api/v1")
app.include_router(source.router, prefix="/api/v1")
app.include_router(ai.router, prefix="/api/v1")
app.include_router(report.router, prefix="/api/v1")
app.include_router(cron.router, prefix="/api/v1")


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
                        "status": "up",
                    }
                }
            },
        }
    },
)
async def health_check() -> dict:
    return {"status": "up"}


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
    logger.info(f"Request to {request.url.path} started")
    response = await call_next(request)
    process_time = time.time() - start_time
    logger.info(f"Request to {request.url.path} took {process_time:.4f} seconds")

    return response


handler = Mangum(app)

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
