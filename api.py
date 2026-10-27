import asyncio
import logging
import os

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from mcp import ClientSession
from mcp.client.streamable_http import streamable_http_client


# --------------------------------------------------
# Configuration
# --------------------------------------------------

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

MCP_URL = os.environ.get(
    "MCP_URL",
    "http://127.0.0.1:8000/mcp",
)

FRONTEND_URL = os.environ.get("FRONTEND_URL", "").rstrip("/")

CORS_ORIGINS = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "https://devflow-frontend-401o.onrender.com",
]

if FRONTEND_URL:
    CORS_ORIGINS.append(FRONTEND_URL)


# --------------------------------------------------
# FastAPI application
# --------------------------------------------------

app = FastAPI(title="DevFlow API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# --------------------------------------------------
# Request model
# --------------------------------------------------

class ExplainRequest(BaseModel):
    error_message: str


# --------------------------------------------------
# Health check
# --------------------------------------------------

@app.get("/api/health")
async def health():
    return {
        "status": "ok",
        "service": "DevFlow API",
    }


# --------------------------------------------------
# Explain error endpoint
# --------------------------------------------------


@app.post("/api/explain")
async def explain(request_body: ExplainRequest):
    error_message = request_body.error_message.strip()

    if not error_message:
        raise HTTPException(
            status_code=400,
            detail="Please enter an error message.",
        )

    for attempt in range(1, 4):
        try:
            logger.info(
                "MCP request attempt %s/3",
                attempt,
            )

            async with streamable_http_client(MCP_URL) as (
                read_stream,
                write_stream,
            ):
                async with ClientSession(
                    read_stream,
                    write_stream,
                ) as session:
                    await session.initialize()

                    result = await session.call_tool(
                        "explain_error",
                        {"error_message": error_message},
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

                    if not explanation.strip():
                        raise HTTPException(
                            status_code=502,
                            detail="The MCP service returned an empty explanation.",
                        )

                    return {"explanation": explanation}

        except HTTPException:
            raise

        except Exception as exc:
            logger.exception(
                "MCP attempt %s/3 failed",
                attempt,
            )

            if attempt == 3:
                raise HTTPException(
                    status_code=502,
                    detail=(
                        "The MCP service is temporarily unavailable. "
                        "Please try again shortly."
                    ),
                ) from exc

            await asyncio.sleep(2 ** attempt)

    raise HTTPException(
        status_code=502,
        detail="The MCP service is temporarily unavailable.",
    )


# --------------------------------------------------
# Local development entry point
# --------------------------------------------------

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        app,
        host="0.0.0.0",
        port=int(os.environ.get("PORT", "10000")),
    )
