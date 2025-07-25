from google.adk.agents.llm_agent import LlmAgent

from tools.fi_tools import financial_data_toolkit

# Clean agent definition for deployment with MCP session persistence
root_agent = LlmAgent(
    model='gemini-2.0-flash',
    name='financial_assistant',
    description='A helpful financial assistant that can access Fi Money data',
    instruction="""You are a financial assistant that helps users with their financial data. 
    You can access their Fi Money account data including transactions, net worth, credit reports, and more.
    Always be helpful and provide clear, actionable financial insights.""",
    tools=[
        financial_data_toolkit
    ]
)
