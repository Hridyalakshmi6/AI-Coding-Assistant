
from mcp.server.mcpserver import MCPServer

mcp = MCPServer("DevFlow")


ERROR_GUIDES = {
    "nullpointerexception": (
        "Java tried to use an object reference that is null. "
        "Initialize the object or check for null before using it."
    ),
    "arrayindexoutofboundsexception": (
        "Java accessed an array position that does not exist. "
        "Check the array length and index."
    ),
    "indexoutofboundsexception": (
        "Java accessed an invalid array or collection index. "
        "Check the index against the valid range."
    ),
    "indexerror": (
        "Python tried to access an invalid list, tuple, or sequence "
        "index. Check the sequence length and index value."
    ),
    "keyerror": (
        "Python could not find the requested dictionary key. "
        "Check the key spelling or use dict.get() when appropriate."
    ),
    "typeerror": (
        "An operation received a value of an incompatible type. "
        "Check variable types and convert values when necessary."
    ),
    "nameerror": (
        "Python could not find the referenced variable or name. "
        "Check its spelling, definition, and scope."
    ),
    "referenceerror": (
        "JavaScript referenced a variable that is unavailable. "
        "Check its declaration, spelling, and scope."
    ),
    "attributeerror": (
        "Python tried to access an attribute or method that the "
        "object does not have. Check the object's type and name."
    ),
    "valueerror": (
        "A function received a value of the correct type but an "
        "invalid value. Check the input and expected format."
    ),
    "zerodivisionerror": (
        "Python attempted to divide by zero. Check the denominator "
        "before performing the division."
    ),
    "modulenotfounderror": (
        "Python could not find an imported module. Check the module "
        "name and install the required package in your environment."
    ),
    "importerror": (
        "Python could not import the requested module or name. "
        "Check the import statement and package installation."
    ),
    "filenotfounderror": (
        "Python could not find the requested file. Check the path, "
        "filename, and current working directory."
    ),
    "indentationerror": (
        "Python indentation is inconsistent or incorrect. "
        "Check indentation levels and use consistent spacing."
    ),
    "syntaxerror": (
        "The code does not follow the language's syntax rules. "
        "Check brackets, quotes, punctuation, and keywords."
    ),
    "recursionerror": (
        "Python exceeded its recursion limit. Check whether a "
        "recursive function has a correct stopping condition."
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
        "variable values and types, and reproduce the issue with "
        "a small test. Share the relevant code for more help."
    )


if __name__ == "__main__":
    mcp.run(transport="streamable-http", port=8000)