"""Scoring and ranking helpers for task prioritization in the CLI app."""

from datetime import datetime

from .models import TaskPriority, TaskStatus


def calculate_task_score(task, current_user_id=None):
    """Calculate a priority score for a task based on multiple factors.

    Args:
        task (Task): Task instance to score.
        current_user_id (str | None): Current user ID for assignment boosts.

    Returns:
        int: Aggregate score where higher means more urgent or important.

    Raises:
        AttributeError: If `task` is missing expected attributes.

    Example:
        >>> from datetime import datetime, timedelta
        >>> from .models import Task, TaskPriority
        >>> t = Task("Fix bug", priority=TaskPriority.HIGH, due_date=datetime.now() + timedelta(days=1))
        >>> calculate_task_score(t) > 0
        True

    Notes:
        The weighting is heuristic and should be calibrated to your team's needs.
        Due-date weights favor near-term deadlines and overdue work.
    """
    # Base priority weights
    priority_weights = {
        TaskPriority.LOW: 1,
        TaskPriority.MEDIUM: 2,
        TaskPriority.HIGH: 4,
        TaskPriority.URGENT: 6
    }

    # Calculate base score from priority
    score = priority_weights.get(task.priority, 0) * 10

    due_date_weights = {
        "overdue": 35,
        "today": 20,
        "next_2_days": 15,
        "next_week": 10,
    }

    # Add due date factor (higher score for tasks due sooner)
    if task.due_date:
        days_until_due = (task.due_date - datetime.now()).days
        if days_until_due < 0:  # Overdue tasks
            score += due_date_weights["overdue"]
        elif days_until_due == 0:  # Due today
            score += due_date_weights["today"]
        elif days_until_due <= 2:  # Due in next 2 days
            score += due_date_weights["next_2_days"]
        elif days_until_due <= 7:  # Due in next week
            score += due_date_weights["next_week"]
    # Reduce score for tasks that are completed or in review
    if task.status == TaskStatus.DONE:
        score -= 50
    elif task.status == TaskStatus.REVIEW:
        score -= 15

    # Boost score for tasks with certain tags
    if any(tag in ["blocker", "critical", "urgent"] for tag in task.tags):
        score += 8

    # Boost score when task is assigned to current user
    if current_user_id is not None:
        assigned_to = getattr(task, "assigned_to", None)
        if assigned_to == current_user_id:
            score += 12

    # Boost score for recently updated tasks
    update_delta = datetime.now() - task.updated_at
    days_since_update = update_delta.days
    if days_since_update < 1:
        score += 5

    return score

def sort_tasks_by_importance(tasks):
    """Sort tasks by calculated importance score (highest first).

    Args:
        tasks (list[Task]): Tasks to sort.

    Returns:
        list[Task]: Tasks ordered by decreasing importance score.

    Raises:
        AttributeError: If any task is missing expected attributes.

    Example:
        >>> from .models import Task
        >>> tasks = [Task("A"), Task("B")]
        >>> sorted_tasks = sort_tasks_by_importance(tasks)
        >>> len(sorted_tasks) == 2
        True

    Notes:
        The scoring uses `calculate_task_score()` and is computed once per task.
    """
    # Calculate scores once and sort by the score
    task_scores = [(calculate_task_score(task), task) for task in tasks]
    sorted_tasks = [task for _, task in sorted(task_scores, reverse=True)]
    return sorted_tasks

def get_top_priority_tasks(tasks, limit=5):
    """Return the top N priority tasks.

    Args:
        tasks (list[Task]): Tasks to rank.
        limit (int): Maximum number of tasks to return.

    Returns:
        list[Task]: Up to `limit` tasks with the highest scores.

    Raises:
        AttributeError: If any task is missing expected attributes.

    Example:
        >>> from .models import Task
        >>> tasks = [Task("A"), Task("B")]
        >>> top = get_top_priority_tasks(tasks, limit=1)
        >>> len(top) == 1
        True

    Notes:
        Passing `limit=0` returns an empty list. Negative limits follow Python
        slicing semantics and may return all but the last N items.
    """
    sorted_tasks = sort_tasks_by_importance(tasks)
    return sorted_tasks[:limit]