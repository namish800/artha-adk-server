from google.adk.agents.llm_agent import LlmAgent

from tools.charts_tools import charts_toolkit
from tools.fi_tools import financial_data_toolkit

# Clean agent definition for deployment with MCP session persistence
root_agent = LlmAgent(
    model='gemini-2.0-flash',
    name='chart_assistant',
    description='A helpful chart assistant that can generate charts for users',
    instruction="""You are a chart assistant that helps users generate charts for their financial data. 
    """,
    tools=[
        charts_toolkit,
        financial_data_toolkit
    ]
)
