from typing import Dict, Any, Optional
from google.adk.agents.llm_agent import Agent

from tools import fi_toolset
from financial_profile_agent.prompts import financial_profile_agent_prompt_2

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

root_agent = Agent(
    model='gemini-2.5-pro',
    name='financial_profile_agent',
    description='A helpful agent that can analyze the user\'s financial profile',
    instruction=financial_profile_agent_prompt_2,
    tools=[fi_toolset]
)


        



