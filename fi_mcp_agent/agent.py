from typing import Dict, Any, Optional
from google.adk.agents.llm_agent import LlmAgent
from google.adk.tools.mcp_tool.mcp_session_manager import StreamableHTTPConnectionParams
from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset
from google.adk.tools.base_tool import BaseTool
from google.adk.tools.tool_context import ToolContext

# Configure MCP toolset with extended timeouts for streaming scenarios
toolset = MCPToolset(
    connection_params=StreamableHTTPConnectionParams(
        url='https://mcp.fi.money:8080/mcp/stream',
        timeout=60.0*30.0,  # Extended connection timeout
        sse_read_timeout=60.0 * 30.0,  # 30 minutes read timeout for streaming
        terminate_on_close=False,  # Don't terminate server on close for session persistence
        headers=None
    ),
    errlog=None
)

# Clean agent definition for deployment with MCP session persistence
root_agent = LlmAgent(
    model='gemini-2.0-flash',
    name='financial_assistant',
    description='A helpful financial assistant that can access Fi Money data',
    instruction="""You are a financial assistant that helps users with their financial data. 
    You can access their Fi Money account data including transactions, net worth, credit reports, and more.
    Always be helpful and provide clear, actionable financial insights.""",
    tools=[
        toolset
    ]
)