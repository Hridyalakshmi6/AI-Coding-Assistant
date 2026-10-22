import os
from mcp.server.mcpserver import MCPServer
from mcp.server.transport_security import TransportSecuritySettings

mcp = MCPServer("DevFlow")

ERROR_GUIDES = {
    "keyerror": "Python could not find the requested key in a dictionary.",
    "zerodivisionerror": "Python attempted to divide a number by zero.",
    "syntaxerror": "The code contains invalid Python syntax.",
    "arrayindexoutofboundsexception": (
        "Java accessed an array position that does not exist. "
        "Check the array length and index."
    ),
    "indexoutofboundsexception": (
        "Java accessed an invalid array or collection index. "
        "Check the index against the valid range."
    ),
}


@mcp.tool()
def explain_error(error_message: str) -> str:
    """Explain a programming error and suggest debugging steps."""

    if not error_message or not error_message.strip():
        return (
            "Please enter an error message or traceback "
            "so DevFlow can help diagnose the problem."
        )

    error = error_message.lower()

    for error_name, explanation in ERROR_GUIDES.items():
        if error_name in error:
            return (
                f"Error detected: {error_name}\n"
                f"Explanation and fix: {explanation}\n"
                "Next step: Check the traceback, locate the failing "
                "line, and reproduce the issue with a small test."
            )

    return (
        f"Error received: {error_message}\n"
        "DevFlow could not identify this error specifically yet. "
        "Read the full traceback, find the failing line, check "
        "variable values and types, and reproduce the issue "
        "with a small test."
    )


if __name__ == "__main__":
    import os

    port = int(os.environ.get("PORT", "8000"))

    mcp.run(
        transport="streamable-http",
        host="0.0.0.0",
        port=port,
        transport_security=TransportSecuritySettings(
            allowed_hosts=[
                "ai-coding-assistant-d230.onrender.com",
            ],
            allowed_origins=[
                "https://ai-coding-assistant-1-1sfr.onrender.com",
            ],
        ),
    )