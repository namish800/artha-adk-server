"""
Supabase CRUD Tools for Artha Project
Provides comprehensive database operations for all tables in the Artha Supabase project.
"""

import logging
import os
from datetime import datetime
from typing import Dict, List, Optional, Any, Union

from supabase import create_client, Client
from supabase.client import ClientOptions

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SupabaseManager:
    """
    Comprehensive Supabase database manager for the Artha project.
    
    This class provides a complete set of CRUD operations for all tables in the Artha Supabase database,
    including goals, achievements, user states, profiles, and generic table operations.
    
    Environment Variables Required:
        SUPABASE_URL: Your Supabase project URL (e.g., https://xxx.supabase.co)
        SUPABASE_KEY: Your Supabase anon/service role key
    
    Features:
        - Automatic error handling and logging
        - Type hints for better IDE support
        - Specialized methods for each table
        - Generic methods for flexible operations
        - Connection timeout configuration
    
    Example:
        manager = SupabaseManager()
        goals = manager.get_user_goals("user-uuid")
    """

    def __init__(self):
        """
        Initialize Supabase client with environment variables.
        
        Raises:
            ValueError: If SUPABASE_URL or SUPABASE_KEY environment variables are not set
            
        Note:
            The client is configured with 10-second timeouts for both PostgREST and Storage operations.
        """
        self.url = os.environ.get("SUPABASE_URL")
        self.key = os.environ.get("SUPABASE_KEY")

        if not self.url or not self.key:
            raise ValueError("SUPABASE_URL and SUPABASE_KEY environment variables are required")

        # Initialize client with timeout options
        self.client: Client = create_client(
            self.url,
            self.key,
            options=ClientOptions(
                postgrest_client_timeout=10,
                storage_client_timeout=10,
                schema="public"
            )
        )
        logger.info("Supabase client initialized successfully")

    def _handle_response(self, response, operation: str):
        """
        Internal method to handle Supabase API responses and provide consistent error handling.
        
        Args:
            response: The response object from Supabase API call
            operation (str): Description of the operation being performed (for logging)
            
        Returns:
            The data from the response if successful
            
        Raises:
            Exception: If the response indicates an error or contains no data
            
        Note:
            This method automatically logs successful operations and detailed error information.
        """
        if hasattr(response, 'data') and response.data is not None:
            logger.info(f"{operation} successful")
            return response.data
        else:
            error_msg = f"{operation} failed"
            if hasattr(response, 'error') and response.error:
                error_msg += f": {response.error}"
            logger.error(error_msg)
            raise Exception(error_msg)

    # ============= GOALS TABLE OPERATIONS =============

    def create_goal(self, goal_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a new goal in the goals table.
        
        This method creates a new goal record with comprehensive tracking capabilities for both
        financial goals (savings, investments) and habit-based goals (exercise, reading).
        
        Args:
            goal_data (Dict[str, Any]): Dictionary containing goal information with the following structure:
                
                Required fields:
                    user_id (str): UUID of the user creating the goal
                    title (str): Clear, descriptive title of the goal
                    goal_type (str): Type of goal (e.g., 'savings', 'investment', 'habit', 'fitness')
                    category (str): Category for organization (e.g., 'financial', 'health', 'personal')
                
                Optional fields:
                    description (str): Detailed description of the goal
                    status (str): Goal status ('active', 'completed', 'paused') - defaults to 'active'
                    deadline (str): Target completion date in ISO format (YYYY-MM-DD)
                    target_amount (float): Financial target amount for money-based goals
                    current_amount (float): Starting amount - defaults to 0.00
                    monthly_contribution (float): Expected monthly contribution amount
                    target_count (int): Target count for habit-based goals (e.g., days, repetitions)
                    current_count (int): Starting count - defaults to 0
                    frequency (str): How often to track ('daily', 'weekly', 'monthly')
                    xp_value (int): Experience points awarded for completion - defaults to 0
                    ai_metadata (dict): Additional AI-specific data as JSON object
        
        Returns:
            Dict[str, Any]: The created goal record including auto-generated fields:
                - id: Auto-generated unique goal ID
                - created_at: Timestamp when goal was created
                - updated_at: Timestamp when goal was last updated
                - All provided goal_data fields
        
        Raises:
            Exception: If goal creation fails due to validation errors or database issues
            
        Example:
            goal_data = {
                "user_id": "123e4567-e89b-12d3-a456-426614174000",
                "title": "Emergency Fund",
                "description": "Build 6-month emergency fund",
                "goal_type": "savings",
                "category": "financial",
                "target_amount": 15000.00,
                "monthly_contribution": 1000.00,
                "deadline": "2024-12-31"
            }
            new_goal = manager.create_goal(goal_data)
        """
        try:
            response = self.client.table("goals").insert(goal_data).execute()
            return self._handle_response(response, "Goal creation")
        except Exception as e:
            logger.error(f"Error creating goal: {e}")
            raise

    def get_goal(self, goal_id: int) -> Optional[Dict[str, Any]]:
        """
        Retrieve a specific goal by its unique ID.
        
        Args:
            goal_id (int): The unique identifier of the goal to retrieve
            
        Returns:
            Optional[Dict[str, Any]]: Complete goal record if found, None if goal doesn't exist.
                The returned dictionary contains all goal fields:
                - id, user_id, title, description, goal_type, category
                - status, deadline, xp_value
                - target_amount, current_amount, monthly_contribution
                - target_count, current_count, frequency
                - streak_count, best_streak, last_completed
                - ai_metadata, created_at, updated_at
        
        Raises:
            Exception: If database query fails
            
        Example:
            goal = manager.get_goal(123)
            if goal:
                print(f"Goal: {goal['title']} - Progress: {goal['current_amount']}/{goal['target_amount']}")
            else:
                print("Goal not found")
        """
        try:
            response = self.client.table("goals").select("*").eq("id", goal_id).execute()
            data = self._handle_response(response, "Goal retrieval")
            return data[0] if data else None
        except Exception as e:
            logger.error(f"Error getting goal {goal_id}: {e}")
            raise

    def get_user_goals(self, user_id: str, status: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Retrieve all goals belonging to a specific user, optionally filtered by status.
        
        This method returns goals ordered by creation date (newest first) and is ideal for
        displaying user dashboards, progress tracking, and goal management interfaces.
        
        Args:
            user_id (str): UUID of the user whose goals to retrieve
            status (Optional[str]): Filter goals by status. Valid values:
                - 'active': Currently active goals (default if not specified)
                - 'completed': Successfully completed goals
                - 'paused': Temporarily paused goals
                - None: Return all goals regardless of status
                
        Returns:
            List[Dict[str, Any]]: List of goal records ordered by created_at (newest first).
                Each goal dictionary contains all fields from the goals table.
                Returns empty list if user has no goals or no goals match the status filter.
        
        Raises:
            Exception: If database query fails or user_id is invalid
            
        Example:
            # Get all active goals for a user
            active_goals = manager.get_user_goals("user-uuid", "active")
            
            # Get all goals regardless of status
            all_goals = manager.get_user_goals("user-uuid")
            
            # Display goal summary
            for goal in active_goals:
                progress = (goal['current_amount'] / goal['target_amount']) * 100 if goal['target_amount'] else 0
                print(f"{goal['title']}: {progress:.1f}% complete")
        """
        try:
            query = self.client.table("goals").select("*").eq("user_id", user_id)

            if status:
                query = query.eq("status", status)

            response = query.order("created_at", desc=True).execute()
            return self._handle_response(response, "User goals retrieval")
        except Exception as e:
            logger.error(f"Error getting user goals for {user_id}: {e}")
            raise

    def update_goal(self, goal_id: int, updates: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update any fields of an existing goal.
        
        This method allows updating any goal fields and automatically sets the updated_at timestamp.
        Use this for general goal modifications like changing title, description, target amounts, etc.
        
        Args:
            goal_id (int): Unique identifier of the goal to update
            updates (Dict[str, Any]): Dictionary of field names and new values to update.
                Can include any valid goal table fields:
                - title, description, goal_type, category, status
                - deadline, target_amount, current_amount, monthly_contribution
                - target_count, current_count, frequency
                - xp_value, ai_metadata
                
        Returns:
            Dict[str, Any]: The updated goal record with all current field values
            
        Raises:
            Exception: If goal_id doesn't exist or update fails due to validation errors
            
        Note:
            The updated_at field is automatically set to the current timestamp.
            For progress-specific updates, consider using update_goal_progress() instead.
            
        Example:
            # Update goal details
            updates = {
                "title": "Updated Emergency Fund Goal",
                "target_amount": 20000.00,
                "deadline": "2025-06-30",
                "status": "active"
            }
            updated_goal = manager.update_goal(123, updates)
            
            # Update AI metadata
            ai_updates = {
                "ai_metadata": {
                    "difficulty_level": "medium",
                    "suggested_actions": ["increase monthly contribution", "review budget"]
                }
            }
            manager.update_goal(123, ai_updates)
        """
        try:
            # Add updated_at timestamp
            updates["updated_at"] = datetime.now().isoformat()

            response = self.client.table("goals").update(updates).eq("id", goal_id).execute()
            return self._handle_response(response, "Goal update")
        except Exception as e:
            logger.error(f"Error updating goal {goal_id}: {e}")
            raise

    def update_goal_progress(self, goal_id: int, current_amount: Optional[float] = None,
                             current_count: Optional[int] = None) -> Dict[str, Any]:
        """
        Update progress tracking fields for a goal.
        
        This specialized method is designed for frequent progress updates and automatically
        handles timestamps for habit tracking. Use this instead of update_goal() when you're
        specifically updating progress values.
        
        Args:
            goal_id (int): Unique identifier of the goal to update
            current_amount (Optional[float]): New current amount for financial goals.
                Use this for savings goals, investment tracking, debt reduction, etc.
                Should be a positive number representing the current progress toward target_amount.
            current_count (Optional[int]): New current count for habit-based goals.
                Use this for tracking repetitions, days completed, tasks finished, etc.
                Should be a non-negative integer representing progress toward target_count.
                
        Returns:
            Dict[str, Any]: The updated goal record with new progress values and timestamps
            
        Raises:
            Exception: If goal_id doesn't exist or update fails
            
        Note:
            - At least one of current_amount or current_count must be provided
            - When current_count is updated, last_completed is automatically set to current timestamp
            - updated_at is automatically set to current timestamp
            - This method does NOT automatically update streak_count - use separate logic for streaks
            
        Example:
            # Update financial goal progress
            manager.update_goal_progress(123, current_amount=5000.00)
            
            # Update habit goal progress
            manager.update_goal_progress(456, current_count=15)
            
            # Update both (for goals that track both metrics)
            manager.update_goal_progress(789, current_amount=2500.00, current_count=30)
            
            # Check if goal is complete after update
            updated_goal = manager.update_goal_progress(123, current_amount=10000.00)
            if updated_goal['current_amount'] >= updated_goal['target_amount']:
                manager.update_goal(123, {"status": "completed"})
        """
        updates = {"updated_at": datetime.now().isoformat()}

        if current_amount is not None:
            updates["current_amount"] = current_amount

        if current_count is not None:
            updates["current_count"] = current_count
            updates["last_completed"] = datetime.now().isoformat()

        return self.update_goal(goal_id, updates)

    def delete_goal(self, goal_id: int) -> bool:
        """
        Permanently delete a goal from the database.
        
        WARNING: This operation is irreversible. Consider updating the goal status to 'paused' 
        or 'cancelled' instead if you want to preserve the record for historical purposes.
        
        Args:
            goal_id (int): Unique identifier of the goal to delete
            
        Returns:
            bool: True if the goal was successfully deleted
            
        Raises:
            Exception: If goal_id doesn't exist or deletion fails due to database constraints
            
        Example:
            # Delete a goal (use with caution)
            success = manager.delete_goal(123)
            if success:
                print("Goal deleted successfully")
                
            # Alternative: Mark as cancelled instead of deleting
            manager.update_goal(123, {"status": "cancelled"})
        """
        try:
            response = self.client.table("goals").delete().eq("id", goal_id).execute()
            self._handle_response(response, "Goal deletion")
            return True
        except Exception as e:
            logger.error(f"Error deleting goal {goal_id}: {e}")
            raise

    def get_goals_by_category(self, user_id: str, category: str) -> List[Dict[str, Any]]:
        """
        Retrieve all goals for a specific user filtered by category.
        
        This method is useful for organizing goals by type (financial, health, personal, etc.)
        and displaying category-specific dashboards or reports.
        
        Args:
            user_id (str): UUID of the user whose goals to retrieve
            category (str): Category to filter by (e.g., 'financial', 'health', 'personal', 'career')
            
        Returns:
            List[Dict[str, Any]]: List of goal records in the specified category,
                ordered by creation date (newest first). Returns empty list if no goals
                exist in the specified category for the user.
        
        Raises:
            Exception: If database query fails
            
        Example:
            # Get all financial goals
            financial_goals = manager.get_goals_by_category("user-uuid", "financial")
            
            # Calculate total financial targets
            total_target = sum(goal.get('target_amount', 0) for goal in financial_goals)
            total_current = sum(goal.get('current_amount', 0) for goal in financial_goals)
            
            print(f"Financial Goals Progress: ${total_current:,.2f} / ${total_target:,.2f}")
        """
        try:
            response = (self.client.table("goals")
                        .select("*")
                        .eq("user_id", user_id)
                        .eq("category", category)
                        .order("created_at", desc=True)
                        .execute())
            return self._handle_response(response, "Goals by category retrieval")
        except Exception as e:
            logger.error(f"Error getting goals by category {category}: {e}")
            raise

    # ============= ACHIEVEMENTS TABLE OPERATIONS =============

    def create_achievement(self, achievement_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a new achievement record in the achievements table.
        
        Achievements are used to gamify the goal-setting experience and reward users
        for reaching milestones, maintaining streaks, or completing specific challenges.
        
        Args:
            achievement_data (Dict[str, Any]): Dictionary containing achievement information:
                Required fields:
                    user_id (str): UUID of the user earning the achievement
                    title (str): Achievement title (e.g., "First Goal Created", "Savings Streak")
                    
                Optional fields:
                    description (str): Detailed description of the achievement
                    category (str): Achievement category (e.g., 'milestone', 'streak', 'completion')
                    target_value (float): Target value required to unlock (if applicable)
                    current_value (float): Current progress toward target - defaults to 0
                    progress_percentage (float): Completion percentage (0-100)
                    is_completed (bool): Whether achievement is unlocked - defaults to False
                    unlocked_at (str): ISO timestamp when achievement was unlocked
                    ai_metadata (dict): Additional AI-specific data
        
        Returns:
            Dict[str, Any]: The created achievement record with auto-generated fields
        
        Raises:
            Exception: If achievement creation fails
            
        Example:
            achievement_data = {
                "user_id": "user-uuid",
                "title": "Goal Setter",
                "description": "Created your first financial goal",
                "category": "milestone",
                "is_completed": True,
                "unlocked_at": datetime.now().isoformat()
            }
            new_achievement = manager.create_achievement(achievement_data)
        """
        try:
            response = self.client.table("achievements").insert(achievement_data).execute()
            return self._handle_response(response, "Achievement creation")
        except Exception as e:
            logger.error(f"Error creating achievement: {e}")
            raise

    def get_user_achievements(self, user_id: str, is_completed: Optional[bool] = None) -> List[Dict[str, Any]]:
        """
        Retrieve achievements for a specific user, optionally filtered by completion status.
        
        This method is essential for displaying user progress, unlocked badges, and
        available achievements in gamification systems.
        
        Args:
            user_id (str): UUID of the user whose achievements to retrieve
            is_completed (Optional[bool]): Filter by completion status:
                - True: Only show unlocked/completed achievements
                - False: Only show locked/incomplete achievements  
                - None: Show all achievements regardless of status
                
        Returns:
            List[Dict[str, Any]]: List of achievement records ordered by creation date (newest first).
                Each achievement contains fields like id, title, description, progress_percentage,
                is_completed, unlocked_at, etc.
        
        Raises:
            Exception: If database query fails
            
        Example:
            # Get all unlocked achievements
            unlocked = manager.get_user_achievements("user-uuid", is_completed=True)
            
            # Get achievements still in progress
            in_progress = manager.get_user_achievements("user-uuid", is_completed=False)
            
            # Display achievement summary
            print(f"Unlocked: {len(unlocked)} achievements")
            for achievement in unlocked:
                print(f"🏆 {achievement['title']}: {achievement['description']}")
        """
        try:
            query = self.client.table("achievements").select("*").eq("user_id", user_id)

            if is_completed is not None:
                query = query.eq("is_completed", is_completed)

            response = query.order("created_at", desc=True).execute()
            return self._handle_response(response, "User achievements retrieval")
        except Exception as e:
            logger.error(f"Error getting user achievements for {user_id}: {e}")
            raise

    def unlock_achievement(self, achievement_id: int) -> Dict[str, Any]:
        """
        Mark an achievement as completed/unlocked and set the unlock timestamp.
        
        This method is typically called when a user meets the criteria for an achievement,
        such as completing their first goal, maintaining a streak, or reaching a milestone.
        
        Args:
            achievement_id (int): Unique identifier of the achievement to unlock
            
        Returns:
            Dict[str, Any]: The updated achievement record with is_completed=True,
                unlocked_at timestamp, and updated_at timestamp
        
        Raises:
            Exception: If achievement_id doesn't exist or update fails
            
        Example:
            # Unlock an achievement when user completes first goal
            unlocked_achievement = manager.unlock_achievement(456)
            
            # Send notification to user
            print(f"🎉 Achievement Unlocked: {unlocked_achievement['title']}!")
            
            # Award XP or other rewards based on achievement
            if 'xp_reward' in unlocked_achievement.get('ai_metadata', {}):
                xp_earned = unlocked_achievement['ai_metadata']['xp_reward']
                # Update user's total XP...
        """
        updates = {
            "is_completed": True,
            "unlocked_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }

        try:
            response = self.client.table("achievements").update(updates).eq("id", achievement_id).execute()
            return self._handle_response(response, "Achievement unlock")
        except Exception as e:
            logger.error(f"Error unlocking achievement {achievement_id}: {e}")
            raise

    # ============= USER_STATES TABLE OPERATIONS =============

    def get_user_state(self, app_name: str, user_id: str) -> Optional[Dict[str, Any]]:
        """Get user state for a specific app.
        
        Args:
            app_name: Application name
            user_id: User ID
            
        Returns:
            User state data or None if not found
        """
        try:
            response = (self.client.table("user_states")
                        .select("*")
                        .eq("app_name", app_name)
                        .eq("user_id", user_id)
                        .execute())
            data = self._handle_response(response, "User state retrieval")
            return data[0] if data else None
        except Exception as e:
            logger.error(f"Error getting user state for {app_name}/{user_id}: {e}")
            raise

    def upsert_user_state(self, app_name: str, user_id: str, state: Dict[str, Any]) -> Dict[str, Any]:
        """Create or update user state.
        
        Args:
            app_name: Application name
            user_id: User ID
            state: State data as JSON
            
        Returns:
            User state data
        """
        try:
            state_data = {
                "app_name": app_name,
                "user_id": user_id,
                "state": state,
                "update_time": datetime.now().isoformat()
            }

            response = (self.client.table("user_states")
                        .upsert(state_data, on_conflict="app_name,user_id")
                        .execute())
            return self._handle_response(response, "User state upsert")
        except Exception as e:
            logger.error(f"Error upserting user state for {app_name}/{user_id}: {e}")
            raise

    # ============= PROFILES TABLE OPERATIONS =============

    def get_profile(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get user profile.
        
        Args:
            user_id: User UUID
            
        Returns:
            Profile data or None if not found
        """
        try:
            response = self.client.table("profiles").select("*").eq("id", user_id).execute()
            data = self._handle_response(response, "Profile retrieval")
            return data[0] if data else None
        except Exception as e:
            logger.error(f"Error getting profile for {user_id}: {e}")
            raise

    def update_profile(self, user_id: str, updates: Dict[str, Any]) -> Dict[str, Any]:
        """Update user profile.
        
        Args:
            user_id: User UUID
            updates: Dictionary of fields to update
            
        Returns:
            Updated profile data
        """
        try:
            updates["updated_at"] = datetime.now().isoformat()

            response = self.client.table("profiles").update(updates).eq("id", user_id).execute()
            return self._handle_response(response, "Profile update")
        except Exception as e:
            logger.error(f"Error updating profile for {user_id}: {e}")
            raise

    # ============= GENERIC TABLE OPERATIONS =============

    def select_from_table(self, table_name: str, columns: str = "*",
                          filters: Optional[Dict[str, Any]] = None,
                          order_by: Optional[str] = None,
                          limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """Generic select operation for any table.
        
        Args:
            table_name: Name of the table
            columns: Columns to select (default: "*")
            filters: Dictionary of column:value filters
            order_by: Column to order by
            limit: Maximum number of records
            
        Returns:
            List of records
        """
        try:
            query = self.client.table(table_name).select(columns)

            if filters:
                for column, value in filters.items():
                    query = query.eq(column, value)

            if order_by:
                query = query.order(order_by)

            if limit:
                query = query.limit(limit)

            response = query.execute()
            return self._handle_response(response, f"Select from {table_name}")
        except Exception as e:
            logger.error(f"Error selecting from {table_name}: {e}")
            raise

    def insert_into_table(self, table_name: str, data: Union[Dict[str, Any], List[Dict[str, Any]]]) -> List[
        Dict[str, Any]]:
        """Generic insert operation for any table.
        
        Args:
            table_name: Name of the table
            data: Data to insert (single record or list of records)
            
        Returns:
            Inserted data
        """
        try:
            response = self.client.table(table_name).insert(data).execute()
            return self._handle_response(response, f"Insert into {table_name}")
        except Exception as e:
            logger.error(f"Error inserting into {table_name}: {e}")
            raise

    def update_table(self, table_name: str, updates: Dict[str, Any],
                     filters: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generic update operation for any table.
        
        Args:
            table_name: Name of the table
            updates: Dictionary of fields to update
            filters: Dictionary of column:value filters for WHERE clause
            
        Returns:
            Updated data
        """
        try:
            query = self.client.table(table_name).update(updates)

            for column, value in filters.items():
                query = query.eq(column, value)

            response = query.execute()
            return self._handle_response(response, f"Update {table_name}")
        except Exception as e:
            logger.error(f"Error updating {table_name}: {e}")
            raise

    def delete_from_table(self, table_name: str, filters: Dict[str, Any]) -> bool:
        """Generic delete operation for any table.
        
        Args:
            table_name: Name of the table
            filters: Dictionary of column:value filters for WHERE clause
            
        Returns:
            True if deleted successfully
        """
        try:
            query = self.client.table(table_name).delete()

            for column, value in filters.items():
                query = query.eq(column, value)

            response = query.execute()
            self._handle_response(response, f"Delete from {table_name}")
            return True
        except Exception as e:
            logger.error(f"Error deleting from {table_name}: {e}")
            raise

    # ============= UTILITY METHODS =============

    def execute_raw_sql(self, query: str) -> List[Dict[str, Any]]:
        """Execute raw SQL query (use with caution).
        
        Args:
            query: SQL query string
            
        Returns:
            Query results
        """
        try:
            response = self.client.rpc('execute_sql', {'query': query}).execute()
            return self._handle_response(response, "Raw SQL execution")
        except Exception as e:
            logger.error(f"Error executing raw SQL: {e}")
            raise

    def get_table_count(self, table_name: str, filters: Optional[Dict[str, Any]] = None) -> int:
        """Get count of records in a table.
        
        Args:
            table_name: Name of the table
            filters: Optional filters
            
        Returns:
            Number of records
        """
        try:
            query = self.client.table(table_name).select("*", count="exact")

            if filters:
                for column, value in filters.items():
                    query = query.eq(column, value)

            response = query.execute()
            return response.count if hasattr(response, 'count') else 0
        except Exception as e:
            logger.error(f"Error getting count from {table_name}: {e}")
            raise


# ============= CONVENIENCE FUNCTIONS =============

# Global instance for easy access
_supabase_manager = None


def get_supabase_manager() -> SupabaseManager:
    """Get or create global SupabaseManager instance."""
    global _supabase_manager
    if _supabase_manager is None:
        _supabase_manager = SupabaseManager()
    return _supabase_manager


# Quick access functions for common operations
def create_goal(goal_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Convenience function to create a goal using the global SupabaseManager instance.
    
    This is a shortcut for manager.create_goal() that automatically handles the
    SupabaseManager initialization and provides the same functionality.
    
    Args:
        goal_data (Dict[str, Any]): Goal data dictionary (see SupabaseManager.create_goal for details)
        
    Returns:
        Dict[str, Any]: Created goal record
        
    Example:
        from tools.supabase_tools import create_goal
        
        goal = create_goal({
            "user_id": "user-uuid",
            "title": "Save $5000",
            "goal_type": "savings",
            "category": "financial",
            "target_amount": 5000.00
        })
    """
    return get_supabase_manager().create_goal(goal_data)


def get_user_goals(user_id: str, status: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    Convenience function to get user goals using the global SupabaseManager instance.
    
    Args:
        user_id (str): User UUID
        status (Optional[str]): Optional status filter ('active', 'completed', 'paused')
        
    Returns:
        List[Dict[str, Any]]: List of user goals
        
    Example:
        from tools.supabase_tools import get_user_goals
        
        active_goals = get_user_goals("user-uuid", "active")
        all_goals = get_user_goals("user-uuid")
    """
    return get_supabase_manager().get_user_goals(user_id, status)


def update_goal_progress(goal_id: int, current_amount: Optional[float] = None,
                         current_count: Optional[int] = None) -> Dict[str, Any]:
    """
    Convenience function to update goal progress using the global SupabaseManager instance.
    
    Args:
        goal_id (int): Goal ID to update
        current_amount (Optional[float]): New current amount for financial goals
        current_count (Optional[int]): New current count for habit goals
        
    Returns:
        Dict[str, Any]: Updated goal record
        
    Example:
        from tools.supabase_tools import update_goal_progress
        
        # Update savings progress
        updated_goal = update_goal_progress(123, current_amount=2500.00)
        
        # Update habit progress
        updated_goal = update_goal_progress(456, current_count=7)
    """
    return get_supabase_manager().update_goal_progress(goal_id, current_amount, current_count)


def get_user_achievements(user_id: str, is_completed: Optional[bool] = None) -> List[Dict[str, Any]]:
    """
    Convenience function to get user achievements using the global SupabaseManager instance.
    
    Args:
        user_id (str): User UUID
        is_completed (Optional[bool]): Filter by completion status
        
    Returns:
        List[Dict[str, Any]]: List of user achievements
        
    Example:
        from tools.supabase_tools import get_user_achievements
        
        unlocked = get_user_achievements("user-uuid", is_completed=True)
        all_achievements = get_user_achievements("user-uuid")
    """
    return get_supabase_manager().get_user_achievements(user_id, is_completed)


def unlock_achievement(achievement_id: int) -> Dict[str, Any]:
    """
    Convenience function to unlock an achievement using the global SupabaseManager instance.
    
    Args:
        achievement_id (int): Achievement ID to unlock
        
    Returns:
        Dict[str, Any]: Updated achievement record
        
    Example:
        from tools.supabase_tools import unlock_achievement
        
        unlocked = unlock_achievement(789)
        print(f"🎉 {unlocked['title']} unlocked!")
    """
    return get_supabase_manager().unlock_achievement(achievement_id)


if __name__ == "__main__":
    # Example usage
    try:
        # Initialize manager
        manager = SupabaseManager()

        # Example: Create a goal
        sample_goal = {
            "user_id": "123e4567-e89b-12d3-a456-426614174000",
            "title": "Save for Emergency Fund",
            "description": "Build an emergency fund of $10,000",
            "goal_type": "savings",
            "category": "financial",
            "target_amount": 10000.00,
            "current_amount": 0.00,
            "monthly_contribution": 500.00
        }

        print("Supabase CRUD tools loaded successfully!")
        print("Available methods:")
        print("- Goals: create_goal, get_goal, get_user_goals, update_goal, delete_goal")
        print("- Achievements: create_achievement, get_user_achievements, unlock_achievement")
        print("- User States: get_user_state, upsert_user_state")
        print("- Profiles: get_profile, update_profile")
        print("- Generic: select_from_table, insert_into_table, update_table, delete_from_table")

    except Exception as e:
        print(f"Error initializing Supabase manager: {e}")
        print("Make sure SUPABASE_URL and SUPABASE_KEY environment variables are set.")
