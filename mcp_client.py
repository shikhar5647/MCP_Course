from mcp import ClientSession, types, StdioServerParameters 
from mcp.client.stdio import stdio_client

server_params = StdioServerParameters(
    command="uv",  # Executable
    args=["run example_server.py"],  # Command line arguments
    env=None,  # Optional environment variables
)

