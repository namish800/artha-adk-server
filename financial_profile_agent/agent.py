from typing import Dict, Any, Optional
from google.adk.agents.callback_context import CallbackContext
from google.adk.agents.llm_agent import Agent
from google.genai import types

from tools import fi_toolset
from financial_profile_agent.prompts import financial_profile_agent_prompt_2, financial_profile_agent_prompt_3
from tools.memory_tools import memory_toolkit
from memory.service import service as memory_service
# spending_analyzer_agent = Agent(
#     model='gemini-2.0-flash',
#     name='spending_analyzer',
#     description='A helpful agent that can analyze the user\'s spending behavior',
#     instruction=spending_analyzer_prompt,
#     tools=[toolset]
# )

# life_stage_agent = Agent(
#     model='gemini-2.0-flash',
#     name='life_stage_agent',
#     description='A helpful agent that can analyze the user\'s life stage',
#     instruction=life_stage_agent_prompt,
#     tools=[toolset]
# )

async def modify_output_after_agent(callback_context: CallbackContext) -> Optional[types.Content]:
    session = callback_context._invocation_context.session
    if len(session.events) >= 2:
        await memory_service.add_session_to_memory(session)

root_agent = Agent(
    model='gemini-2.5-pro',
    name='financial_profile_agent',
    description='A helpful agent that can analyze the user\'s financial profile',
    instruction=financial_profile_agent_prompt_3,
    tools=[fi_toolset, memory_toolkit]
)


        



