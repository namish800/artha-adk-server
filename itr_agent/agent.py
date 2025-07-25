from typing import Dict, Any, Optional
from google.adk.agents.llm_agent import Agent
from tools import browser_toolset
from itr_agent.prompts import itr_process_prompt

def render_session(url: str):
    return f"The live view URL of the session is {url}"

root_agent = Agent(
    model='gemini-2.5-flash',
    name='itr_agent',
    description='You help user file the ITR on browser',
    instruction=itr_process_prompt,
    tools=[browser_toolset, render_session]
)


        



