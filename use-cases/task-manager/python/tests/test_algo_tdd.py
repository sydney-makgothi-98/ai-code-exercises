from datetime import datetime, timedelta
import sys
from pathlib import Path

# Ensure the package root is on sys.path so relative imports work
sys.path.append(str(Path(__file__).resolve().parents[2]))

from python.algo import calculate_task_score, sort_tasks_by_importance, get_top_priority_tasks
from python.models import Task, TaskPriority, TaskStatus


def _neutralize_task(task):
    task.status = TaskStatus.TODO
    task.due_date = None
    task.tags = []
    task.updated_at = datetime.now() - timedelta(days=2)
    return task


def test_days_since_update_bug_regression():
    task = Task("Old", priority=TaskPriority.MEDIUM)
    task = _neutralize_task(task)
    task.updated_at = datetime.now() - timedelta(days=2, hours=1)

    score = calculate_task_score(task)

    # Should not get recent-update boost when last update was 2+ days ago
    assert score == 20


def test_integration_priority_workflow():
    low = _neutralize_task(Task("Low", priority=TaskPriority.LOW))
    med = _neutralize_task(Task("Medium", priority=TaskPriority.MEDIUM))
    high = _neutralize_task(Task("High", priority=TaskPriority.HIGH))

    sorted_tasks = sort_tasks_by_importance([low, high, med])
    assert [t.title for t in sorted_tasks] == ["High", "Medium", "Low"]

    top = get_top_priority_tasks([low, high, med], limit=2)
    assert [t.title for t in top] == ["High", "Medium"]
