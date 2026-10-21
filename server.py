
from mcp.server.mcpserver import MCPServer

mcp = MCPServer("DevFlow")


@mcp.tool()
def explain_error(error_message: str) -> str:
    """Explain a programming error and suggest debugging steps."""

    error = error_message.lower()

    if "nullpointerexception" in error:
        return (
            "A NullPointerException occurs when Java code tries "
            "to use an object reference that is null. "
            "Check where the object is initialized and add a "
            "null check before using it."
        )

    if "indexoutofboundsexception" in error:
        return (
            "An IndexOutOfBoundsException means your code is "
            "accessing an invalid list or array index. "
            "Check the index and ensure it is within valid bounds."
        )

    if "syntaxerror" in error or "syntax error" in error:
        return (
            "A SyntaxError means the code does not follow the "
            "language's syntax rules. Check brackets, quotes, "
            "colons, and spelling."
        )

    if "indentationerror" in error:
        return (
            "An IndentationError means Python indentation is "
            "incorrect. Check spaces and indentation levels."
        )

    return (
        f"Error received: {error_message}\n"
        "Start by reading the full traceback, identifying the "
        "line where the error occurs, checking variable values, "
        "and reproducing the issue with a small test."
    )


if __name__ == "__main__":
    mcp.run(transport="streamable-http", port=8000)
