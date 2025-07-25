from google.adk.tools.mcp_tool.mcp_session_manager import StreamableHTTPConnectionParams
from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset

# Configure financial data toolkit with extended timeouts for streaming scenarios
financial_data_toolkit = MCPToolset(
    connection_params=StreamableHTTPConnectionParams(
        url='https://mcp.fi.money:8080/mcp/stream',
        timeout=60.0 * 30.0,  # Extended connection timeout
        sse_read_timeout=60.0 * 30.0,  # 30 minutes read timeout for streaming
        terminate_on_close=False,  # Don't terminate server on close for session persistence
        headers=None
    ),
    errlog=None
)
