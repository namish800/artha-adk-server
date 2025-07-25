from google.adk.agents.llm_agent import Agent

from tools.aikar_tools import (
    calculate_income_tax,
    calculate_capital_gains_tax,
    compare_tax_regimes
)
from tools.fi_tools import financial_data_toolkit
from .prompts import tax_calculator_agent_prompt

root_agent = Agent(
    model='gemini-2.5-pro',
    name='tax_calculator_agent',
    description='You are a helpful agent that can calculate the tax of the user\'s income.',
    instruction=tax_calculator_agent_prompt,
    tools=[
        financial_data_toolkit,
        # Tax calculation functions
        calculate_income_tax,
        calculate_capital_gains_tax,
        compare_tax_regimes,
    ]
)
