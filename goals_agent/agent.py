from google.adk.agents.llm_agent import Agent

from tools.fi_tools import financial_data_toolkit
from tools.supabase_tools import (
    create_goal,
    get_goal,
    get_user_goals,
    update_goal,
    update_goal_progress,
    delete_goal,
    get_goals_by_category,
    create_achievement,
    get_achievement,
    get_user_achievements,
    get_achievements_by_category,
    update_achievement,
    unlock_achievement,
    delete_achievement,
    get_user_total_points,
    get_goal_completion_rate,
)
from .prompts import goals_agent_prompt

root_agent = Agent(
    model='gemini-2.5-pro',
    name='goals_agent',
    description='You are a helpful agent that can analyze the user\'s financial goals and provide insights and recommendations.',
    instruction=goals_agent_prompt,
    tools=[
        financial_data_toolkit,
        # Goals CRUD operations
        create_goal,
        get_goal,
        get_user_goals,
        update_goal,
        update_goal_progress,
        delete_goal,
        get_goals_by_category,
        # Achievements CRUD operations
        create_achievement,
        get_achievement,
        get_user_achievements,
        get_achievements_by_category,
        update_achievement,
        unlock_achievement,
        delete_achievement,
        # Utility functions
        get_user_total_points,
        get_goal_completion_rate,
    ]
)
