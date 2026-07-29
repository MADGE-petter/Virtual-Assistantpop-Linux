"""
Agent Logging Utility - Dùng chung cho tất cả Agents
Chuyển từ AppHandler để đảm bảo Habit Tracking không bị mất
"""
from datetime import datetime


def log_app_opened(app_name: str, user_name: str = "user", user_id: int = 1):
    """Log ứng dụng được mở qua analytics service và habit tracker"""
    actual_user_id = user_id
    if actual_user_id == 1 and user_name and user_name not in ("user", "bạn"):
        try:
            from model.Sql import SqlService
            actual_user_id = SqlService().db.get_or_create_user(user_name)
        except Exception:
            actual_user_id = user_id

    try:
        from service.analytics_service import get_analytics_service
        analytics = get_analytics_service(user_name or "user")
        analytics.log_app_opened(app_name)
    except Exception as e:
        print(f"[AgentLogger] Analytics log error: {e}")
    
    # Log cho habit tracker (học thói quen)
    try:
        from controller.habit_tracker import get_habit_tracker
        habit_tracker = get_habit_tracker()
        habit_tracker.log_app_opened(actual_user_id, app_name)
        print(f"[HabitTracker] Logged: {app_name} at {datetime.now().strftime('%H:%M')}")
    except Exception as e:
        print(f"[AgentLogger] Habit tracker error: {e}")