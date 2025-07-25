import os
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
from supabase import create_client, Client
from google.adk.tools import ToolContext

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# Initialize Supabase client
def get_supabase_client() -> Client:
    """Initialize and return Supabase client"""
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_KEY")

    if not url or not key:
        raise ValueError("SUPABASE_URL and SUPABASE_KEY environment variables are required")

    return create_client(url, key)


# ============================================================================
# GOALS TABLE CRUD OPERATIONS
# ============================================================================

def create_goal(
        title: str,
        tool_context: ToolContext,
        description: Optional[str] = None,
        category: Optional[str] = None,
        target_amount: Optional[float] = None,
        current_amount: float = 0.0,
        target_date: Optional[str] = None,
        status: str = "active",
        frequency: Optional[str] = None,
        streak_count: int = 0
) -> Dict[str, Any]:
    """
    Create a new goal for a user in the goals table.
    
    This function creates a financial or habit goal with tracking capabilities.
    Goals can have target amounts, deadlines, categories, and progress tracking.
    The user_id is automatically fetched from the ToolContext state.
    
    Args:
        title (str): The title/name of the goal. Required.
        tool_context (ToolContext): The tool context containing user state and session info. Required.
        description (str, optional): Detailed description of the goal. Defaults to None.
        category (str, optional): Category of the goal (e.g., 'savings', 'fitness', 'learning'). Defaults to None.
        target_amount (float, optional): Target amount to achieve (for financial goals). Defaults to None.
        current_amount (float, optional): Current progress amount. Defaults to 0.0.
        target_date (str, optional): Target completion date in ISO format (YYYY-MM-DD). Defaults to None.
        status (str, optional): Goal status ('active', 'paused', 'completed'). Defaults to 'active'.
        frequency (str, optional): Frequency for habit goals ('daily', 'weekly', 'monthly'). Defaults to None.
        streak_count (int, optional): Current streak count for habit goals. Defaults to 0.
    
    Returns:
        Dict[str, Any]: The created goal object with all fields including auto-generated ID, 
                       created_at timestamp, and other database fields. Returns None if creation fails.
    
    Raises:
        ValueError: If SUPABASE_URL or SUPABASE_KEY environment variables are missing, or if user_id not found in context.
        Exception: If database operation fails or network issues occur.
    
    Example:
        >>> goal = create_goal(
        ...     title="Save for vacation",
        ...     tool_context=tool_context,
        ...     description="Save $5000 for Europe trip",
        ...     category="savings",
        ...     target_amount=5000.0,
        ...     target_date="2024-12-31"
        ... )
        >>> print(goal['id'])  # Returns the generated goal ID
    """
    try:
        # Fetch user_id from ToolContext state
        user = tool_context.state.to_dict()
        user_id = user["user_id"]
        if not user_id:
            raise ValueError("user_id not found in ToolContext state. User authentication required.")

        supabase = get_supabase_client()

        goal_data = {
            "user_id": user_id,
            "title": title,
            "description": description,
            "category": category,
            "target_amount": target_amount,
            "current_amount": current_amount,
            "target_date": target_date,
            "status": status,
            "frequency": frequency,
            "streak_count": streak_count,
            "is_completed": False
        }

        # Remove None values
        goal_data = {k: v for k, v in goal_data.items() if v is not None}

        result = supabase.table("goals").insert(goal_data).execute()
        logger.info(f"Created goal: {title} for user: {user_id}")
        return result.data[0] if result.data else None

    except Exception as e:
        logger.error(f"Error creating goal: {str(e)}")
        raise


def get_goal(goal_id: str) -> Optional[Dict[str, Any]]:
    """
    Retrieve a specific goal by its unique ID.
    
    This function fetches a single goal record from the database using the goal's ID.
    Useful for getting detailed information about a specific goal.
    
    Args:
        goal_id (str): The unique identifier of the goal to retrieve. Required.
    
    Returns:
        Optional[Dict[str, Any]]: The goal object containing all fields (id, user_id, title, 
                                 description, category, target_amount, current_amount, 
                                 target_date, status, frequency, streak_count, is_completed, 
                                 created_at, updated_at). Returns None if goal not found.
    
    Raises:
        ValueError: If SUPABASE_URL or SUPABASE_KEY environment variables are missing.
        Exception: If database operation fails or network issues occur.
    
    Example:
        >>> goal = get_goal("goal_123")
        >>> if goal:
        ...     print(f"Goal: {goal['title']}, Progress: {goal['current_amount']}/{goal['target_amount']}")
        ... else:
        ...     print("Goal not found")
    """
    try:
        supabase = get_supabase_client()
        result = supabase.table("goals").select("*").eq("id", goal_id).execute()

        if result.data:
            logger.info(f"Retrieved goal: {goal_id}")
            return result.data[0]
        return None

    except Exception as e:
        logger.error(f"Error retrieving goal {goal_id}: {str(e)}")
        raise


def get_user_goals(tool_context: ToolContext, status: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    Retrieve all goals for the current user, with optional status filtering.
    
    This function fetches all goals belonging to the current user, ordered by creation date (newest first).
    Can be filtered by goal status to get only active, completed, or paused goals.
    The user_id is automatically fetched from the ToolContext state.
    
    Args:
        tool_context (ToolContext): The tool context containing user state and session info. Required.
        status (str, optional): Filter goals by status ('active', 'completed', 'paused'). 
                               If None, returns all goals regardless of status. Defaults to None.
    
    Returns:
        List[Dict[str, Any]]: List of goal objects, each containing all goal fields. 
                             Returns empty list if no goals found. Goals are ordered by 
                             created_at timestamp (newest first).
    
    Raises:
        ValueError: If SUPABASE_URL or SUPABASE_KEY environment variables are missing, or if user_id not found in context.
        Exception: If database operation fails or network issues occur.
    
    Example:
        >>> # Get all goals for current user
        >>> all_goals = get_user_goals(tool_context)
        >>> print(f"User has {len(all_goals)} total goals")
        >>> 
        >>> # Get only active goals
        >>> active_goals = get_user_goals(tool_context, status="active")
        >>> print(f"User has {len(active_goals)} active goals")
    """
    try:
        # Fetch user_id from ToolContext state
        user = tool_context.state.to_dict()
        user_id = user["user_id"]
        if not user_id:
            raise ValueError("user_id not found in ToolContext state. User authentication required.")

        supabase = get_supabase_client()
        query = supabase.table("goals").select("*").eq("user_id", user_id)

        if status:
            query = query.eq("status", status)

        result = query.order("created_at", desc=True).execute()
        logger.info(f"Retrieved {len(result.data)} goals for user: {user_id}")
        return result.data

    except Exception as e:
        logger.error(f"Error retrieving goals for user {user_id}: {str(e)}")
        raise


def get_goals_by_category(tool_context: ToolContext, category: str) -> List[Dict[str, Any]]:
    """
    Retrieve all goals for the current user filtered by a specific category.
    
    This function fetches goals belonging to the current user that match a specific category.
    Useful for organizing and displaying goals by type (e.g., financial, fitness, learning).
    The user_id is automatically fetched from the ToolContext state.
    
    Args:
        tool_context (ToolContext): The tool context containing user state and session info. Required.
        category (str): The category to filter by (e.g., 'savings', 'fitness', 'learning', 
                       'career', 'health'). Required.
    
    Returns:
        List[Dict[str, Any]]: List of goal objects matching the specified category. 
                             Returns empty list if no goals found in that category.
    
    Raises:
        ValueError: If SUPABASE_URL or SUPABASE_KEY environment variables are missing, or if user_id not found in context.
        Exception: If database operation fails or network issues occur.
    
    Example:
        >>> # Get all savings goals
        >>> savings_goals = get_goals_by_category(tool_context, "savings")
        >>> for goal in savings_goals:
        ...     print(f"Savings goal: {goal['title']} - ${goal['current_amount']}/${goal['target_amount']}")
        >>> 
        >>> # Get all fitness goals
        >>> fitness_goals = get_goals_by_category(tool_context, "fitness")
    """
    try:
        # Fetch user_id from ToolContext state
        user = tool_context.state.to_dict()
        user_id = user["user_id"]
        if not user_id:
            raise ValueError("user_id not found in ToolContext state. User authentication required.")

        supabase = get_supabase_client()
        result = supabase.table("goals").select("*").eq("user_id", user_id).eq("category", category).execute()
        logger.info(f"Retrieved {len(result.data)} goals in category '{category}' for user: {user_id}")
        return result.data

    except Exception as e:
        logger.error(f"Error retrieving goals by category for user {user_id}: {str(e)}")
        raise


def update_goal(goal_id: str, updates: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """
    Update a goal with new data fields.
    
    This function updates any fields of an existing goal. The updated_at timestamp 
    is automatically set to the current time. Can update any goal field including 
    title, description, target amounts, status, etc.
    
    Args:
        goal_id (str): The unique identifier of the goal to update. Required.
        updates (Dict[str, Any]): Dictionary containing the fields to update and their new values.
                                 Can include any goal field: 'title', 'description', 'category',
                                 'target_amount', 'current_amount', 'target_date', 'status',
                                 'frequency', 'streak_count', 'is_completed'. Required.
    
    Returns:
        Optional[Dict[str, Any]]: The updated goal object with all fields including the new 
                                 updated_at timestamp. Returns None if goal not found or update fails.
    
    Raises:
        ValueError: If SUPABASE_URL or SUPABASE_KEY environment variables are missing.
        Exception: If database operation fails or network issues occur.
    
    Example:
        >>> # Update goal title and target amount
        >>> updated_goal = update_goal("goal_123", {
        ...     "title": "Save for dream vacation",
        ...     "target_amount": 6000.0,
        ...     "description": "Updated target for Europe trip"
        ... })
        >>> 
        >>> # Mark goal as completed
        >>> completed_goal = update_goal("goal_123", {
        ...     "status": "completed",
        ...     "is_completed": True
        ... })
    """
    try:
        supabase = get_supabase_client()

        # Add updated_at timestamp
        updates["updated_at"] = datetime.utcnow().isoformat()

        result = supabase.table("goals").update(updates).eq("id", goal_id).execute()

        if result.data:
            logger.info(f"Updated goal: {goal_id}")
            return result.data[0]
        return None

    except Exception as e:
        logger.error(f"Error updating goal {goal_id}: {str(e)}")
        raise


def update_goal_progress(goal_id: str, current_amount: float, streak_count: Optional[int] = None) -> Optional[
    Dict[str, Any]]:
    """
    Update the progress of a goal with automatic completion detection.
    
    This function updates the current progress amount and optionally the streak count.
    It automatically marks the goal as completed if the current amount reaches or exceeds
    the target amount. This is a specialized function for progress tracking.
    
    Args:
        goal_id (str): The unique identifier of the goal to update progress for. Required.
        current_amount (float): The new current progress amount. Required.
        streak_count (int, optional): The new streak count for habit goals. If None, 
                                     streak count is not updated. Defaults to None.
    
    Returns:
        Optional[Dict[str, Any]]: The updated goal object with new progress values and 
                                 potentially updated completion status. Returns None if 
                                 goal not found or update fails.
    
    Raises:
        ValueError: If SUPABASE_URL or SUPABASE_KEY environment variables are missing.
        Exception: If database operation fails or network issues occur.
    
    Example:
        >>> # Update savings goal progress
        >>> updated_goal = update_goal_progress("goal_123", 3500.0)
        >>> print(f"Progress: ${updated_goal['current_amount']}/${updated_goal['target_amount']}")
        >>> 
        >>> # Update habit goal with streak
        >>> habit_goal = update_goal_progress("habit_456", 15.0, streak_count=7)
        >>> print(f"Streak: {habit_goal['streak_count']} days")
    """
    try:
        updates = {"current_amount": current_amount}

        if streak_count is not None:
            updates["streak_count"] = streak_count

        # Check if goal is completed
        goal = get_goal(goal_id)
        if goal and goal.get("target_amount") and current_amount >= goal["target_amount"]:
            updates["is_completed"] = True
            updates["status"] = "completed"

        return update_goal(goal_id, updates)

    except Exception as e:
        logger.error(f"Error updating goal progress {goal_id}: {str(e)}")
        raise


def delete_goal(goal_id: str) -> bool:
    """
    Delete a goal from the database.
    
    This function permanently removes a goal from the database. This action cannot be undone.
    Use with caution as all goal data including progress history will be lost.
    
    Args:
        goal_id (str): The unique identifier of the goal to delete. Required.
    
    Returns:
        bool: True if the goal was successfully deleted, False if goal was not found 
              or deletion failed.
    
    Raises:
        ValueError: If SUPABASE_URL or SUPABASE_KEY environment variables are missing.
        Exception: If database operation fails or network issues occur.
    
    Example:
        >>> # Delete a goal
        >>> success = delete_goal("goal_123")
        >>> if success:
        ...     print("Goal deleted successfully")
        ... else:
        ...     print("Goal not found or deletion failed")
    """
    try:
        supabase = get_supabase_client()
        result = supabase.table("goals").delete().eq("id", goal_id).execute()

        if result.data:
            logger.info(f"Deleted goal: {goal_id}")
            return True
        return False

    except Exception as e:
        logger.error(f"Error deleting goal {goal_id}: {str(e)}")
        raise


# ============================================================================
# ACHIEVEMENTS TABLE CRUD OPERATIONS
# ============================================================================

def create_achievement(
        title: str,
        tool_context: ToolContext,
        description: Optional[str] = None,
        category: Optional[str] = None,
        badge_icon: Optional[str] = None,
        points: int = 0,
        is_unlocked: bool = False
) -> Dict[str, Any]:
    """
    Create a new achievement for the current user in the achievements table.
    
    This function creates an achievement badge that can be unlocked by users.
    Achievements are part of the gamification system and can award points to users.
    They can be created in locked state and unlocked later when conditions are met.
    The user_id is automatically fetched from the ToolContext state.
    
    Args:
        title (str): The title/name of the achievement. Required.
        tool_context (ToolContext): The tool context containing user state and session info. Required.
        description (str, optional): Detailed description of what the achievement represents. Defaults to None.
        category (str, optional): Category of the achievement (e.g., 'savings', 'streak', 'milestone'). Defaults to None.
        badge_icon (str, optional): Icon identifier or URL for the achievement badge. Defaults to None.
        points (int, optional): Points awarded when this achievement is unlocked. Defaults to 0.
        is_unlocked (bool, optional): Whether the achievement starts in unlocked state. Defaults to False.
    
    Returns:
        Dict[str, Any]: The created achievement object with all fields including auto-generated ID,
                       created_at timestamp, and other database fields. Returns None if creation fails.
    
    Raises:
        ValueError: If SUPABASE_URL or SUPABASE_KEY environment variables are missing, or if user_id not found in context.
        Exception: If database operation fails or network issues occur.
    
    Example:
        >>> achievement = create_achievement(
        ...     title="First Goal Creator",
        ...     tool_context=tool_context,
        ...     description="Created your first financial goal",
        ...     category="milestone",
        ...     badge_icon="🎯",
        ...     points=50
        ... )
        >>> print(achievement['id'])  # Returns the generated achievement ID
    """
    try:
        # Fetch user_id from ToolContext state
        user = tool_context.state.to_dict()
        user_id = user["user_id"]
        if not user_id:
            raise ValueError("user_id not found in ToolContext state. User authentication required.")

        supabase = get_supabase_client()

        achievement_data = {
            "user_id": user_id,
            "title": title,
            "description": description,
            "category": category,
            "badge_icon": badge_icon,
            "points": points,
            "is_unlocked": is_unlocked
        }

        # Remove None values
        achievement_data = {k: v for k, v in achievement_data.items() if v is not None}

        result = supabase.table("achievements").insert(achievement_data).execute()
        logger.info(f"Created achievement: {title} for user: {user_id}")
        return result.data[0] if result.data else None

    except Exception as e:
        logger.error(f"Error creating achievement: {str(e)}")
        raise


def get_achievement(achievement_id: str) -> Optional[Dict[str, Any]]:
    """
    Retrieve a specific achievement by its unique ID.
    
    This function fetches a single achievement record from the database using the achievement's ID.
    Useful for getting detailed information about a specific achievement including its unlock status.
    
    Args:
        achievement_id (str): The unique identifier of the achievement to retrieve. Required.
    
    Returns:
        Optional[Dict[str, Any]]: The achievement object containing all fields (id, user_id, title,
                                 description, category, badge_icon, points, is_unlocked, 
                                 unlocked_at, created_by_ai_at, created_at, updated_at). 
                                 Returns None if achievement not found.
    
    Raises:
        ValueError: If SUPABASE_URL or SUPABASE_KEY environment variables are missing.
        Exception: If database operation fails or network issues occur.
    
    Example:
        >>> achievement = get_achievement("achievement_123")
        >>> if achievement:
        ...     status = "🔓 Unlocked" if achievement['is_unlocked'] else "🔒 Locked"
        ...     print(f"{status} {achievement['title']} - {achievement['points']} points")
        ... else:
        ...     print("Achievement not found")
    """
    try:
        supabase = get_supabase_client()
        result = supabase.table("achievements").select("*").eq("id", achievement_id).execute()

        if result.data:
            logger.info(f"Retrieved achievement: {achievement_id}")
            return result.data[0]
        return None

    except Exception as e:
        logger.error(f"Error retrieving achievement {achievement_id}: {str(e)}")
        raise


def get_user_achievements(tool_context: ToolContext, is_unlocked: Optional[bool] = None) -> List[Dict[str, Any]]:
    """
    Retrieve all achievements for the current user, with optional unlock status filtering.
    
    This function fetches all achievements belonging to the current user, ordered by creation date (newest first).
    Can be filtered by unlock status to get only unlocked or locked achievements.
    The user_id is automatically fetched from the ToolContext state.
    
    Args:
        tool_context (ToolContext): The tool context containing user state and session info. Required.
        is_unlocked (bool, optional): Filter achievements by unlock status. True for unlocked 
                                     achievements, False for locked achievements. If None, 
                                     returns all achievements regardless of status. Defaults to None.
    
    Returns:
        List[Dict[str, Any]]: List of achievement objects, each containing all achievement fields.
                             Returns empty list if no achievements found. Achievements are ordered
                             by created_at timestamp (newest first).
    
    Raises:
        ValueError: If SUPABASE_URL or SUPABASE_KEY environment variables are missing, or if user_id not found in context.
        Exception: If database operation fails or network issues occur.
    
    Example:
        >>> # Get all achievements for current user
        >>> all_achievements = get_user_achievements(tool_context)
        >>> print(f"User has {len(all_achievements)} total achievements")
        >>> 
        >>> # Get only unlocked achievements
        >>> unlocked = get_user_achievements(tool_context, is_unlocked=True)
        >>> total_points = sum(a['points'] for a in unlocked)
        >>> print(f"User has {len(unlocked)} unlocked achievements worth {total_points} points")
    """
    try:
        # Fetch user_id from ToolContext state
        user = tool_context.state.to_dict()
        user_id = user["user_id"]
        if not user_id:
            raise ValueError("user_id not found in ToolContext state. User authentication required.")

        supabase = get_supabase_client()
        query = supabase.table("achievements").select("*").eq("user_id", user_id)

        if is_unlocked is not None:
            query = query.eq("is_unlocked", is_unlocked)

        result = query.order("created_at", desc=True).execute()
        logger.info(f"Retrieved {len(result.data)} achievements for user: {user_id}")
        return result.data

    except Exception as e:
        logger.error(f"Error retrieving achievements for user {user_id}: {str(e)}")
        raise


def get_achievements_by_category(tool_context: ToolContext, category: str) -> List[Dict[str, Any]]:
    """
    Retrieve all achievements for the current user filtered by a specific category.
    
    This function fetches achievements belonging to the current user that match a specific category.
    Useful for organizing and displaying achievements by type (e.g., savings milestones, streaks).
    The user_id is automatically fetched from the ToolContext state.
    
    Args:
        tool_context (ToolContext): The tool context containing user state and session info. Required.
        category (str): The category to filter by (e.g., 'savings', 'streak', 'milestone', 
                       'completion', 'consistency'). Required.
    
    Returns:
        List[Dict[str, Any]]: List of achievement objects matching the specified category.
                             Returns empty list if no achievements found in that category.
    
    Raises:
        ValueError: If SUPABASE_URL or SUPABASE_KEY environment variables are missing, or if user_id not found in context.
        Exception: If database operation fails or network issues occur.
    
    Example:
        >>> # Get all savings-related achievements
        >>> savings_achievements = get_achievements_by_category(tool_context, "savings")
        >>> for achievement in savings_achievements:
        ...     status = "✅" if achievement['is_unlocked'] else "⏳"
        ...     print(f"{status} {achievement['title']} - {achievement['points']} points")
        >>> 
        >>> # Get all streak achievements
        >>> streak_achievements = get_achievements_by_category(tool_context, "streak")
    """
    try:
        # Fetch user_id from ToolContext state
        user = tool_context.state.to_dict()
        user_id = user["user_id"]
        if not user_id:
            raise ValueError("user_id not found in ToolContext state. User authentication required.")

        supabase = get_supabase_client()
        result = supabase.table("achievements").select("*").eq("user_id", user_id).eq("category", category).execute()
        logger.info(f"Retrieved {len(result.data)} achievements in category '{category}' for user: {user_id}")
        return result.data

    except Exception as e:
        logger.error(f"Error retrieving achievements by category for user {user_id}: {str(e)}")
        raise


def update_achievement(achievement_id: str, updates: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """
    Update an achievement with new data fields.
    
    This function updates any fields of an existing achievement. The updated_at timestamp
    is automatically set to the current time. Can update any achievement field including
    title, description, points, unlock status, etc.
    
    Args:
        achievement_id (str): The unique identifier of the achievement to update. Required.
        updates (Dict[str, Any]): Dictionary containing the fields to update and their new values.
                                 Can include any achievement field: 'title', 'description', 
                                 'category', 'badge_icon', 'points', 'is_unlocked', 
                                 'unlocked_at'. Required.
    
    Returns:
        Optional[Dict[str, Any]]: The updated achievement object with all fields including the new
                                 updated_at timestamp. Returns None if achievement not found or update fails.
    
    Raises:
        ValueError: If SUPABASE_URL or SUPABASE_KEY environment variables are missing.
        Exception: If database operation fails or network issues occur.
    
    Example:
        >>> # Update achievement title and points
        >>> updated_achievement = update_achievement("achievement_123", {
        ...     "title": "Super Saver",
        ...     "points": 100,
        ...     "description": "Saved over $10,000 in total"
        ... })
        >>> 
        >>> # Manually unlock an achievement
        >>> unlocked_achievement = update_achievement("achievement_123", {
        ...     "is_unlocked": True,
        ...     "unlocked_at": "2024-01-15T10:30:00Z"
        ... })
    """
    try:
        supabase = get_supabase_client()

        # Add updated_at timestamp
        updates["updated_at"] = datetime.utcnow().isoformat()

        result = supabase.table("achievements").update(updates).eq("id", achievement_id).execute()

        if result.data:
            logger.info(f"Updated achievement: {achievement_id}")
            return result.data[0]
        return None

    except Exception as e:
        logger.error(f"Error updating achievement {achievement_id}: {str(e)}")
        raise


def unlock_achievement(achievement_id: str) -> Optional[Dict[str, Any]]:
    """
    Unlock an achievement and set the unlock timestamp.
    
    This function marks an achievement as unlocked and records the unlock timestamp.
    This is a specialized function for the gamification system when achievement
    conditions are met. The user will receive the points associated with this achievement.
    
    Args:
        achievement_id (str): The unique identifier of the achievement to unlock. Required.
    
    Returns:
        Optional[Dict[str, Any]]: The updated achievement object with is_unlocked=True and
                                 unlocked_at timestamp set. Returns None if achievement not found
                                 or unlock fails.
    
    Raises:
        ValueError: If SUPABASE_URL or SUPABASE_KEY environment variables are missing.
        Exception: If database operation fails or network issues occur.
    
    Example:
        >>> # Unlock an achievement when user completes their first goal
        >>> unlocked = unlock_achievement("achievement_123")
        >>> if unlocked:
        ...     print(f"🎉 Achievement unlocked: {unlocked['title']}!")
        ...     print(f"You earned {unlocked['points']} points!")
        ... else:
        ...     print("Failed to unlock achievement")
    """
    try:
        updates = {
            "is_unlocked": True,
            "unlocked_at": datetime.utcnow().isoformat()
        }

        return update_achievement(achievement_id, updates)

    except Exception as e:
        logger.error(f"Error unlocking achievement {achievement_id}: {str(e)}")
        raise


def delete_achievement(achievement_id: str) -> bool:
    """
    Delete an achievement from the database.
    
    This function permanently removes an achievement from the database. This action cannot be undone.
    Use with caution as all achievement data including unlock history will be lost.
    Note: Deleting unlocked achievements will also remove the points from the user's total.
    
    Args:
        achievement_id (str): The unique identifier of the achievement to delete. Required.
    
    Returns:
        bool: True if the achievement was successfully deleted, False if achievement was not found
              or deletion failed.
    
    Raises:
        ValueError: If SUPABASE_URL or SUPABASE_KEY environment variables are missing.
        Exception: If database operation fails or network issues occur.
    
    Example:
        >>> # Delete an achievement
        >>> success = delete_achievement("achievement_123")
        >>> if success:
        ...     print("Achievement deleted successfully")
        ... else:
        ...     print("Achievement not found or deletion failed")
    """
    try:
        supabase = get_supabase_client()
        result = supabase.table("achievements").delete().eq("id", achievement_id).execute()

        if result.data:
            logger.info(f"Deleted achievement: {achievement_id}")
            return True
        return False

    except Exception as e:
        logger.error(f"Error deleting achievement {achievement_id}: {str(e)}")
        raise


# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def get_user_total_points(tool_context: ToolContext) -> int:
    """
    Calculate the total points earned by the current user from all unlocked achievements.
    
    This function retrieves all unlocked achievements for the current user and sums up their points.
    This is useful for displaying user progress, leaderboards, or determining user level/rank
    in the gamification system. The user_id is automatically fetched from the ToolContext state.
    
    Args:
        tool_context (ToolContext): The tool context containing user state and session info. Required.
    
    Returns:
        int: The total points earned from all unlocked achievements. Returns 0 if user has
             no unlocked achievements or no achievements at all.
    
    Raises:
        ValueError: If SUPABASE_URL or SUPABASE_KEY environment variables are missing, or if user_id not found in context.
        Exception: If database operation fails or network issues occur.
    
    Example:
        >>> total_points = get_user_total_points(tool_context)
        >>> print(f"User has earned {total_points} total points")
        >>> 
        >>> # Use for user level calculation
        >>> if total_points >= 1000:
        ...     print("🏆 Gold Level User!")
        >>> elif total_points >= 500:
        ...     print("🥈 Silver Level User!")
        >>> else:
        ...     print("🥉 Bronze Level User!")
    """
    try:
        achievements = get_user_achievements(tool_context, is_unlocked=True)
        total_points = sum(achievement.get("points", 0) for achievement in achievements)

        # Get user_id for logging
        user = tool_context.state.to_dict()
        user_id = user.get("user_id", "unknown")
        logger.info(f"User {user_id} has {total_points} total points")
        return total_points

    except Exception as e:
        user = tool_context.state.to_dict()
        user_id = user.get("user_id", "unknown")
        logger.error(f"Error calculating total points for user {user_id}: {str(e)}")
        raise


def get_goal_completion_rate(tool_context: ToolContext) -> float:
    """
    Calculate the goal completion rate percentage for the current user.
    
    This function calculates what percentage of the current user's goals have been completed.
    It considers all goals (regardless of status) and determines how many are marked
    as completed. This is useful for user progress analytics and motivation.
    The user_id is automatically fetched from the ToolContext state.
    
    Args:
        tool_context (ToolContext): The tool context containing user state and session info. Required.
    
    Returns:
        float: The completion rate as a percentage (0.0 to 100.0). Returns 0.0 if user has
               no goals or all goals are incomplete. Returns 100.0 if all goals are completed.
    
    Raises:
        ValueError: If SUPABASE_URL or SUPABASE_KEY environment variables are missing, or if user_id not found in context.
        Exception: If database operation fails or network issues occur.
    
    Example:
        >>> completion_rate = get_goal_completion_rate(tool_context)
        >>> print(f"User has completed {completion_rate:.1f}% of their goals")
        >>> 
        >>> # Use for progress feedback
        >>> if completion_rate >= 80:
        ...     print("🌟 Excellent progress! You're crushing your goals!")
        >>> elif completion_rate >= 50:
        ...     print("👍 Good progress! Keep it up!")
        >>> else:
        ...     print("💪 You've got this! Focus on completing your current goals.")
    """
    try:
        all_goals = get_user_goals(tool_context)
        if not all_goals:
            return 0.0

        completed_goals = [goal for goal in all_goals if goal.get("is_completed", False)]
        completion_rate = len(completed_goals) / len(all_goals) * 100

        # Get user_id for logging
        user = tool_context.state.to_dict()
        user_id = user.get("user_id", "unknown")
        logger.info(f"User {user_id} has {completion_rate:.1f}% goal completion rate")
        return completion_rate

    except Exception as e:
        user = tool_context.state.to_dict()
        user_id = user.get("user_id", "unknown")
        logger.error(f"Error calculating completion rate for user {user_id}: {str(e)}")
        raise
