# Intentionally broken Python. Discoverer should log a warning and yield zero
# tools rather than crashing the scan.
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("broken")

@mcp.tool(
def busted(:
    return None
