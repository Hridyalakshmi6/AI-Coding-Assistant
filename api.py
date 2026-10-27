
import asyncio
import logging
import os

from fastapi import FastAPI, HTTPException, Request
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

FRONTEND_URL = os.environ.get("FRONTEND_URL", "")

CORS_ORIGINS = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "https://devflow-frontend-401o.onrender.com",
]

if FRONTEND_URL:
    CORS_ORIGINS.append(FRONTEND_URL)


# --------------------------------------------------
# MCP connection and application lifecycle
# --------------------------------------------------

@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """
    Connect to the MCP server with retries.

    The API starts only after MCP initializes successfully.
    Temporary connection failures are retried.
    """

    app.state.mcp_session = None

    max_attempts = 5

    for attempt in range(1, max_attempts + 1):
        try:
            logger.info(
                "Connecting to MCP server (attempt %s/%s)",
                attempt,
                max_attempts,
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

                    app.state.mcp_session = session

                    logger.info(
                        "MCP session initialized successfully."
                    )

                    try:
                        yield
                    finally:
                        app.state.mcp_session = None

                    return

        except asyncio.CancelledError:
            raise

        except Exception:
            logger.exception(
                "MCP connection failed (attempt %s/%s)",
                attempt,
                max_attempts,
            )

            if attempt == max_attempts:
                logger.critical(
                    "Could not connect to MCP server after %s attempts.",
                    max_attempts,
                )
                raise

            delay = min(2 ** attempt, 16)

            logger.info("Retrying MCP connection in %s seconds.", delay)

            await asyncio.sleep(delay)


# --------------------------------------------------
# FastAPI application
# --------------------------------------------------

app = FastAPI(
    title="DevFlow API"
)

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
    session_available = getattr(
        app.state,
        "mcp_session",
        None,
    ) is not None

    return {
        "status": "ok" if session_available else "degraded",
        "service": "DevFlow API",
        "mcp_connected": session_available,
    }


# --------------------------------------------------
# Explain error endpoint
# --------------------------------------------------


@app.post("/api/explain")
async def explain(request_body: ExplainRequest):
    if not request_body.error_message.strip():
        raise HTTPException(
            status_code=400,
            detail="Please enter an error message.",
        )

    try:
        # Create a fresh connection and session for this request.
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
                    {
                        "error_message": request_body.error_message,
                    },
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
        logger.exception("MCP connection or tool call failed")
        raise HTTPException(
            status_code=502,
            detail="Failed to communicate with the MCP service. Please try again.",
        ) from exc


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
