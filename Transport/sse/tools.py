from fastmcp import FastMCP

mcp = FastMCP("Arithmetic Tools")

@mcp.tool()
def add(a: int, b: int) -> int:
    "Adds two numbers a, b"
    return a + b

@mcp.tool()
def subtract(a: int, b: int) -> int:
    "Subtracts b from a"
    return a - b

@mcp.tool()
def multiply(a: int, b: int) -> int:
    "Multiplies two numbers a, b"
    return a * b

@mcp.tool()
def divide(a: int, b: int) -> float:
    "Divides a by b"
    if b == 0:
        raise ValueError("Cannot divide by zero")
    return a / b

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "dev":
        mcp.run()
    else:
        mcp.run(transport="sse")