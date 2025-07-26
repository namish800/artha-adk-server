from google.adk.tools.mcp_tool.mcp_session_manager import StreamableHTTPConnectionParams
from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset

import os

fi_mcp_url = os.getenv('FI_MCP_URL')

# Configure financial data toolkit with extended timeouts for streaming scenarios
financial_data_toolkit = MCPToolset(
    connection_params=StreamableHTTPConnectionParams(
        url=fi_mcp_url,
        timeout=60.0 * 30.0,  # Extended connection timeout
        sse_read_timeout=60.0 * 30.0,  # 30 minutes read timeout for streaming
        terminate_on_close=False,  # Don't terminate server on close for session persistence
        headers=None
    ),
    errlog=None
)
