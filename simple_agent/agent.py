import json
from typing import Optional
from google.adk.agents.callback_context import CallbackContext
from google.adk.agents.llm_agent import LlmAgent
from google.adk.sessions.session import Session
from google.adk.tools.tool_context import ToolContext
from google.genai import types

from memory.service import service as memory_service

import json

def get_state(tool_context: ToolContext):
    msg = json.dumps(tool_context.state.to_dict(), indent=4)
    
    print(msg)
    return msg


async def modify_output_after_agent(callback_context: CallbackContext) -> Optional[types.Content]:
    session: Session = callback_context._invocation_context.session
    # print(json.dumps(session, indent=4))
    if len(session.events) >= 2:
        print("*"*40)
        print("Adding session to memory")
        print("*"*40)
        await memory_service.add_session_to_memory(session)

# Clean agent definition for deployment with MCP session persistence
root_agent = LlmAgent(
    model='gemini-2.0-flash',
    name='financial_assistant',
    description='A helpful financial assistant that can access Fi Money data',
    instruction="""call the tools as requested by the user""",
    tools=[
        get_state
    ],
    after_agent_callback=modify_output_after_agent
)
