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
                    "BROWSERBASE_API_KEY": os.getenv("BROWSERBASE_API_KEY"),
                    "BROWSERBASE_PROJECT_ID": os.getenv("BROWSERBASE_PROJECT_ID"),
                    "GEMINI_API_KEY": os.getenv("GEMINI_API_KEY")
                }
            )
connection_params = StdioConnectionParams(
    server_params=server_params,
    timeout=60.0*30.0,
)

toolset = MCPToolset(
            connection_params=connection_params,
        )