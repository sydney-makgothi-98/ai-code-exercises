from datetime import datetime

from models import TaskStatus, TaskPriority

def calculate_task_score(task):
    """Calculate a priority score for a task based on multiple factors."""
    now = datetime.now()
    # Base priority weights
    priority_weights = {
        TaskPriority.LOW: 1,
        TaskPriority.MEDIUM: 2,
        TaskPriority.HIGH: 4,
        TaskPriority.URGENT: 6
    }

    # Calculate base score from priority
    score = priority_weights.get(task.priority, 0) * 10

    # Add due date factor (higher score for tasks due sooner)
    if task.due_date:
        days_until_due = (task.due_date - now).total_seconds() / 86400
        if days_until_due < 0:  # Overdue tasks
            score += 35
        elif days_until_due <= 0:  # Due today
            score += 20
        elif days_until_due <= 2:  # Due in next 2 days
            score += 15
        elif days_until_due <= 7:  # Due in next week
            score += 10

    # Reduce score for tasks that are completed or in review
    if task.status == TaskStatus.DONE:
        score -= 50
    elif task.status == TaskStatus.REVIEW:
        score -= 15

    # Boost score for tasks with certain tags
    tag_set = {tag.lower() for tag in task.tags}
    if tag_set.intersection({"blocker", "critical", "urgent"}):
        score += 8

    # Boost score for recently updated tasks
    seconds_since_update = (now - task.updated_at).total_seconds()
    if seconds_since_update < 86400:
        score += 5

    return score

def sort_tasks_by_importance(tasks):
    """Sort tasks by calculated importance score (highest first)."""
    task_scores = [(calculate_task_score(task), task) for task in tasks]
    # Use key parameter to tell sorted() to only compare the scores (first element of tuple)
    sorted_tasks = [task for _, task in sorted(task_scores, key=lambda x: x[0], reverse=True)]
    return sorted_tasks

def get_top_priority_tasks(tasks, limit=5):
    """Return the top N priority tasks."""
    sorted_tasks = sort_tasks_by_importance(tasks)
    return sorted_tasks[:limit]
