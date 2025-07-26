from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset
from google.adk.tools.mcp_tool.mcp_session_manager import StdioServerParameters, StdioConnectionParams

import os

server_params = StdioServerParameters(
    command='npx',
    args=[
        "-y",
        "@antv/mcp-server-chart"
    ],
)
connection_params = StdioConnectionParams(
    server_params=server_params,
    timeout=60.0*30.0,
)

charts_toolkit = MCPToolset(
    connection_params=connection_params,
)