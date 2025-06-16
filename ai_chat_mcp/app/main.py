from mcp.server.fastmcp import FastMCP
from .tools import ALL_TOOLS


def create_mcp_server() -> FastMCP:

    print("🚀 Initializing Professional MCP Tool Server...")
    mcp = FastMCP("Alva Professional Tool Server")

    for registrar in ALL_TOOLS:
        registrar(mcp)
        print(f"✅ Tools from '{registrar.__module__}' registered.")

    print("🛠️ All tools registered successfully.")
    return mcp

mcp_server = create_mcp_server()

if __name__ == "__main__":
    print("Starting FastMCP server on http://localhost:8000/mcp")
    mcp_server.run(transport="streamable-http")