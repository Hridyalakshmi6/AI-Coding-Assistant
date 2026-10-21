
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from mcp import ClientSession
from mcp.client.streamable_http import streamable_http_client
import os
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

MCP_URL = os.environ.get(
    "MCP_URL",
    "http://127.0.0.1:8000/mcp"
)
app = FastAPI(title="DevFlow API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ExplainRequest(BaseModel):
    error_message: str


@app.get("/api/health")
async def health():
    return {"status": "ok", "service": "DevFlow API"}


@app.post("/api/explain")
async def explain(request: ExplainRequest):
    if not request.error_message.strip():
        raise HTTPException(
            status_code=400,
            detail="Please enter an error message.",
        )

    try:
        async with streamable_http_client(MCP_URL) as (
            read_stream,
            write_stream,
            ):
            async with ClientSession(
                read_stream, write_stream
            ) as session:
                await session.initialize()

                result = await session.call_tool(
                    "explain_error",
                    {"error_message": request.error_message},
                )

                if result.is_error:
                    raise HTTPException(
                        status_code=502,
                        detail="The MCP tool could not process this error.",
                    )

                explanation = "\n".join(
                    item.text
                    for item in result.content
                    if getattr(item, "text", None)
                )

                return {"explanation": explanation}

    except HTTPException:
        raise
    except Exception as exc:
        logger.exception("MCP tool call failed")
        raise HTTPException(
            status_code=502,
            detail=f"MCP tool call failed: {exc}",
        ) from exc

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        app,
        host="0.0.0.0",
        port=int(os.environ.get("PORT", "10000")),
    )