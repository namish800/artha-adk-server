from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset
from google.adk.tools.mcp_tool.mcp_session_manager import StdioServerParameters, StdioConnectionParams

import os

server_params = StdioServerParameters(
                command='npx',
                args=[
                    "-y",
                    "@browserbasehq/mcp",
                    "--proxies"
                ],
                env={
                    "BROWSERBASE_API_KEY": "bb_live_0v1p3jlrC1Uk3_tqv2aojY8NMtk",
                    "BROWSERBASE_PROJECT_ID": "22907d6d-c9a3-4842-930f-59f76067903a",
                    "GEMINI_API_KEY": "AIzaSyCRPS-JHsmOUfeWggUGmR97WbkSsB3wN7s"
                }
            )
connection_params = StdioConnectionParams(
    server_params=server_params,
    timeout=60.0*30.0,
)

toolset = MCPToolset(
            connection_params=connection_params,
        )