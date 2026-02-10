"""Domain models for tasks and related enums."""

# task_manager/models.py
from datetime import datetime
from enum import Enum
import uuid

class TaskPriority(Enum):
    """Priority levels for tasks.

    Notes:
        Values map to increasing urgency. Used in scoring and filtering.
    """
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    URGENT = 4

class TaskStatus(Enum):
    """Lifecycle states for tasks."""
    TODO = "todo"
    IN_PROGRESS = "in_progress"
    REVIEW = "review"
    DONE = "done"
    ABANDONED = "abandoned"

class Task:
    """Task entity with lifecycle and metadata.

    Args:
        title (str): Title of the task.
        description (str): Optional details.
        priority (TaskPriority): Priority level.
        due_date (datetime | None): Optional due date.
        tags (list[str] | None): Optional list of tags.

    Example:
        >>> Task("Write docs")
        <...Task...>

    Notes:
        IDs are generated as UUID4 strings on creation.
    """

    def __init__(self, title, description="", priority=TaskPriority.MEDIUM,
                 due_date=None, tags=None):
        """Initialize a new task instance.

        Args:
            title (str): Task title.
            description (str): Optional description.
            priority (TaskPriority): Priority level.
            due_date (datetime | None): Optional due date.
            tags (list[str] | None): Optional list of tags.

        Returns:
            None
        """
        self.id = str(uuid.uuid4())
        self.title = title
        self.description = description
        self.priority = priority
        self.status = TaskStatus.TODO
        self.created_at = datetime.now()
        self.updated_at = self.created_at
        self.due_date = due_date
        self.completed_at = None
        self.tags = tags or []

    def update(self, **kwargs):
        """Update mutable fields using keyword arguments.

        Args:
            **kwargs: Field-value pairs to update.

        Returns:
            None

        Example:
            >>> task = Task("Do stuff")
            >>> task.update(title="Do more stuff")
        """
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
        self.updated_at = datetime.now()

    def mark_as_done(self):
        """Mark the task as done and stamp completion time.

        Returns:
            None

        Example:
            >>> task = Task("Ship v1")
            >>> task.mark_as_done()
            >>> task.status == TaskStatus.DONE
            True
        """
        self.status = TaskStatus.DONE
        self.completed_at = datetime.now()
        self.updated_at = self.completed_at

    def is_overdue(self):
        """Check if the task is overdue and not completed.

        Returns:
            bool: True when overdue and not done.

        Example:
            >>> task = Task("Pay invoice")
            >>> task.is_overdue()
            False

        Notes:
            Tasks without a due date are never considered overdue.
        """
        if not self.due_date:
            return False
        return self.due_date < datetime.now() and self.status != TaskStatus.DONE

