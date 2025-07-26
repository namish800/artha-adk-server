import json
from google.adk.agents.llm_agent import LlmAgent
from google.adk.tools.tool_context import ToolContext

from tools.fi_tools import financial_data_toolkit

def get_state(tool_context: ToolContext):
    msg = json.dumps(tool_context.state.to_dict(), indent=4)
    
    print(msg)
    return msg


# Clean agent definition for deployment with MCP session persistence
root_agent = LlmAgent(
    model='gemini-2.0-flash',
    name='financial_assistant',
    description='A helpful financial assistant that can access Fi Money data',
    instruction="""call the tools as requested by the user""",
    tools=[
        get_state
    ]
)
