# "mcpServers": {
#   "neo4j": {
#     "command": "uvx",
#     "args": [ "mcp-neo4j-memory@0.2.0" ],
#     "env": {
#       "NEO4J_URL": "neo4j+s://xxxx.databases.neo4j.io",
#       "NEO4J_USERNAME": "<your-username>",
#       "NEO4J_PASSWORD": "<your-password>"
#     }
#   }
# }

from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset
from google.adk.tools.mcp_tool.mcp_session_manager import StdioServerParameters, StdioConnectionParams

import os

server_params = StdioServerParameters(
                command='uvx',
                args=[
                    "mcp-neo4j-memory@0.2.0"
                ],
                env={
                    "NEO4J_URL": os.getenv("NEO4J_URI"),
                    "NEO4J_USERNAME": os.getenv("NEO4J_USER"),
                    "NEO4J_PASSWORD": os.getenv("NEO4J_PASSWORD")
                }
            )
connection_params = StdioConnectionParams(
    server_params=server_params,
    timeout=60.0*30.0,
)

memory_toolkit = MCPToolset(
            connection_params=connection_params,
        )
