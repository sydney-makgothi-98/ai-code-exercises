"""Application layer for task management operations used by the CLI."""

# task_manager/app.py
import argparse
from datetime import datetime, timedelta
from .models import Task, TaskPriority, TaskStatus
from .storage import TaskStorage

class TaskManager:
    """High-level facade for CRUD operations and statistics.

    Args:
        storage_path (str): Path to the JSON file used for persistence.

    Example:
        >>> manager = TaskManager("tasks.json")
        >>> manager.create_task("Draft spec")
        ...

    Notes:
        This class delegates storage concerns to `TaskStorage` and focuses on
        validation, formatting, and derived behavior.
    """

    def __init__(self, storage_path="tasks.json"):
        """Initialize a `TaskManager` with a storage backend.

        Args:
            storage_path (str): File path for persisted tasks.

        Returns:
            None

        Example:
            >>> TaskManager("tasks.json")
            ...
        """
        self.storage = TaskStorage(storage_path)

    def _auto_abandon_overdue(self):
        """Mark stale, low-priority overdue tasks as abandoned.

        Returns:
            None

        Notes:
            Tasks that are overdue by more than 7 days and are not high/urgent
            are automatically moved to `ABANDONED`.
        """
        cutoff = datetime.now() - timedelta(days=7)
        changed = False

        for task in self.storage.get_all_tasks():
            if task.status in (TaskStatus.DONE, TaskStatus.ABANDONED):
                continue
            if not task.due_date or task.due_date >= cutoff:
                continue
            if task.priority in (TaskPriority.HIGH, TaskPriority.URGENT):
                continue

            task.update(status=TaskStatus.ABANDONED)
            changed = True

        if changed:
            self.storage.save()

    def create_task(self, title, description="", priority_value=2,
                   due_date_str=None, tags=None):
        """Create a new task and persist it.

        Args:
            title (str): Task title.
            description (str): Optional task description.
            priority_value (int): Priority value mapped by `TaskPriority`.
            due_date_str (str | None): Due date in YYYY-MM-DD format.
            tags (list[str] | None): Optional list of tag strings.

        Returns:
            str | None: The created task ID, or None when parsing fails.

        Raises:
            ValueError: If `priority_value` is not a valid `TaskPriority`.

        Example:
            >>> manager = TaskManager("tasks.json")
            >>> task_id = manager.create_task("Write docs", priority_value=2)
            >>> isinstance(task_id, str)
            True

        Notes:
            Invalid `due_date_str` is handled by printing an error and
            returning None.
        """
        #There is a magic number here, what does 2 mean? Is it on a scale of 1 to 10, 1 to 5?? Not descriptive enough
        priority = TaskPriority(priority_value)
        due_date = None
        if due_date_str:
            try:
                due_date = datetime.strptime(due_date_str, "%Y-%m-%d")
            except ValueError:
                print("Invalid date format. Use YYYY-MM-DD")
                return None

        task = Task(title, description, priority, due_date, tags)
        task_id = self.storage.add_task(task)
        return task_id

    def list_tasks(self, status_filter=None, priority_filter=None, show_overdue=False):
        """List tasks with optional filters.

        Args:
            status_filter (str | None): Status value to filter by.
            priority_filter (int | None): Priority value to filter by.
            show_overdue (bool): If True, only overdue tasks are returned.

        Returns:
            list[Task]: Matching tasks.

        Raises:
            ValueError: If `status_filter` or `priority_filter` is invalid.

        Example:
            >>> manager = TaskManager("tasks.json")
            >>> manager.list_tasks()
            ...
        """
        self._auto_abandon_overdue()
        if show_overdue:
            return self.storage.get_overdue_tasks()

        if status_filter:
            status = TaskStatus(status_filter)
            return self.storage.get_tasks_by_status(status)

        if priority_filter:
            priority = TaskPriority(priority_filter)
            return self.storage.get_tasks_by_priority(priority)

        return self.storage.get_all_tasks()

    def update_task_status(self, task_id, new_status_value):
        """Update a task's status.

        Args:
            task_id (str): Task ID.
            new_status_value (str): New status value.

        Returns:
            bool: True when updated, False when not found.

        Raises:
            ValueError: If `new_status_value` is invalid.

        Example:
            >>> manager = TaskManager("tasks.json")
            >>> manager.update_task_status("id", "done")
            False
        """
        new_status = TaskStatus(new_status_value)
        if new_status == TaskStatus.DONE:
            task = self.storage.get_task(task_id)
            if task:
                task.mark_as_done()
                self.storage.save()
                return True
        else:
            return self.storage.update_task(task_id, status=new_status)

    def update_task_priority(self, task_id, new_priority_value):
        """Update a task's priority.

        Args:
            task_id (str): Task ID.
            new_priority_value (int): Priority value.

        Returns:
            bool: True when updated, False when not found.

        Raises:
            ValueError: If `new_priority_value` is invalid.

        Example:
            >>> manager = TaskManager("tasks.json")
            >>> manager.update_task_priority("id", 3)
            False
        """
        new_priority = TaskPriority(new_priority_value)
        return self.storage.update_task(task_id, priority=new_priority)

    def update_task_due_date(self, task_id, due_date_str):
        """Update a task's due date.

        Args:
            task_id (str): Task ID.
            due_date_str (str): New due date in YYYY-MM-DD format.

        Returns:
            bool: True when updated, False on invalid input or not found.

        Example:
            >>> manager = TaskManager("tasks.json")
            >>> manager.update_task_due_date("id", "2026-01-01")
            False

        Notes:
            Invalid dates are handled by printing an error and returning False.
        """
        try:
            due_date = datetime.strptime(due_date_str, "%Y-%m-%d")
            return self.storage.update_task(task_id, due_date=due_date)
        except ValueError:
            print("Invalid date format. Use YYYY-MM-DD")
            return False

    def delete_task(self, task_id):
        """Delete a task by ID.

        Args:
            task_id (str): Task ID.

        Returns:
            bool: True if deleted, False if not found.

        Example:
            >>> manager = TaskManager("tasks.json")
            >>> manager.delete_task("id")
            False
        """
        return self.storage.delete_task(task_id)

    def get_task_details(self, task_id):
        """Retrieve a task by ID after applying auto-abandon logic.

        Args:
            task_id (str): Task ID.

        Returns:
            Task | None: The task if found, otherwise None.

        Example:
            >>> manager = TaskManager("tasks.json")
            >>> manager.get_task_details("id") is None
            True
        """
        self._auto_abandon_overdue()
        return self.storage.get_task(task_id)

    def add_tag_to_task(self, task_id, tag):
        """Add a tag to a task if it is not already present.

        Args:
            task_id (str): Task ID.
            tag (str): Tag to add.

        Returns:
            bool: True when updated, False when task not found.

        Example:
            >>> manager = TaskManager("tasks.json")
            >>> manager.add_tag_to_task("id", "urgent")
            False
        """
        task = self.storage.get_task(task_id)
        if task:
            if tag not in task.tags:
                task.tags.append(tag)
                self.storage.save()
            return True
        return False

    def remove_tag_from_task(self, task_id, tag):
        """Remove a tag from a task.

        Args:
            task_id (str): Task ID.
            tag (str): Tag to remove.

        Returns:
            bool: True when removed, False when task or tag not found.

        Example:
            >>> manager = TaskManager("tasks.json")
            >>> manager.remove_tag_from_task("id", "urgent")
            False
        """
        task = self.storage.get_task(task_id)
        if task and tag in task.tags:
            task.tags.remove(tag)
            self.storage.save()
            return True
        return False

    def get_statistics(self):
        """Compute aggregate statistics across all tasks.

        Returns:
            dict: Summary containing total counts and breakdowns.

        Example:
            >>> manager = TaskManager("tasks.json")
            >>> stats = manager.get_statistics()
            >>> "total" in stats
            True

        Notes:
            Status and priority counts include all tasks in storage.
        """
        self._auto_abandon_overdue()
        tasks = self.storage.get_all_tasks()
        total = len(tasks)

        # Count by status
        status_counts = {status.value: 0 for status in TaskStatus}
        for task in tasks:
            status_counts[task.status.value] += 1

        # Count by priority
        priority_counts = {priority.value: 0 for priority in TaskPriority}
        for task in tasks:
            priority_counts[task.priority.value] += 1

        # Count overdue
        overdue_count = len([task for task in tasks if task.is_overdue()])

        # Count completed in last 7 days
        seven_days_ago = datetime.now() - timedelta(days=7)
        completed_recently = len([
            task for task in tasks
            if task.completed_at and task.completed_at >= seven_days_ago
        ])

        return {
            "total": total,
            "by_status": status_counts,
            "by_priority": priority_counts,
            "overdue": overdue_count,
            "completed_last_week": completed_recently
        }

