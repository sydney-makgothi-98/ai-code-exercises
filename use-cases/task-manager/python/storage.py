"""Persistence layer for tasks using JSON serialization."""

# task_manager/storage.py
import json
import os
from datetime import datetime
from .models import Task, TaskPriority, TaskStatus

class TaskEncoder(json.JSONEncoder):
    """JSON encoder that knows how to serialize `Task` objects."""

    def default(self, obj):
        """Convert a `Task` to a JSON-serializable dict.

        Args:
            obj (object): Object to serialize.

        Returns:
            dict: JSON-serializable mapping for tasks.

        Raises:
            TypeError: If object is not JSON serializable.

        Example:
            >>> from .models import Task
            >>> TaskEncoder().default(Task("Write docs"))
            ...
        """
        if isinstance(obj, Task):
            task_dict = obj.__dict__.copy()
            task_dict['priority'] = obj.priority.value
            task_dict['status'] = obj.status.value
            # Convert datetime objects to ISO format strings
            for key in ['created_at', 'updated_at', 'due_date', 'completed_at']:
                if task_dict.get(key) is not None:
                    task_dict[key] = task_dict[key].isoformat()
            return task_dict
        return super().default(obj)

class TaskDecoder(json.JSONDecoder):
    """JSON decoder that reconstructs `Task` objects from dicts."""

    def __init__(self, *args, **kwargs):
        """Initialize the decoder with a custom object hook.

        Returns:
            None
        """
        json.JSONDecoder.__init__(self, object_hook=self.object_hook, *args, **kwargs)

    def object_hook(self, obj):
        """Decode JSON dicts into `Task` instances when possible.

        Args:
            obj (dict): Parsed JSON object.

        Returns:
            Task | dict: Decoded task or original dict.

        Raises:
            ValueError: If priority or status values are invalid.

        Example:
            >>> decoder = TaskDecoder()
            >>> decoder.object_hook({"id": "1", "title": "T", "priority": 2, "status": "todo"})
            ...
        """
        if 'id' in obj and 'title' in obj:
            task = Task(obj['title'], obj.get('description', ''))
            task.id = obj['id']
            task.priority = TaskPriority(obj['priority'])
            task.status = TaskStatus(obj['status'])

            # Convert ISO format strings to datetime objects
            for key in ['created_at', 'updated_at', 'completed_at']:
                if obj.get(key):
                    setattr(task, key, datetime.fromisoformat(obj[key]))

            if obj.get('due_date'):
                task.due_date = datetime.fromisoformat(obj['due_date'])

            task.tags = obj.get('tags', [])
            return task
        return obj

class TaskStorage:
    """Storage service for persisting and querying tasks.

    Args:
        storage_path (str): Path to the JSON file to read/write.

    Example:
        >>> storage = TaskStorage("tasks.json")
        >>> isinstance(storage.get_all_tasks(), list)
        True

    Notes:
        Load and save errors are caught and printed to stdout.
    """

    def __init__(self, storage_path="tasks.json"):
        """Initialize storage and load tasks from disk.

        Args:
            storage_path (str): JSON file path.

        Returns:
            None
        """
        self.storage_path = storage_path
        self.tasks = {}
        self.load()

    def load(self):
        """Load tasks from the storage file into memory.

        Returns:
            None

        Notes:
            Any exceptions during load are caught and printed.
        """
        if os.path.exists(self.storage_path):
            try:
                with open(self.storage_path, 'r') as f:
                    tasks_data = json.load(f, cls=TaskDecoder)
                    if isinstance(tasks_data, list):
                        for task in tasks_data:
                            self.tasks[task.id] = task
            except Exception as e:
                print(f"Error loading tasks: {e}")

    def save(self):
        """Persist tasks to the storage file.

        Returns:
            None

        Notes:
            Any exceptions during save are caught and printed.
        """
        try:
            with open(self.storage_path, 'w') as f:
                json.dump(list(self.tasks.values()), f, cls=TaskEncoder, indent=2)
        except Exception as e:
            print(f"Error saving tasks: {e}")

    def add_task(self, task):
        """Add a task to storage and persist it.

        Args:
            task (Task): Task instance to add.

        Returns:
            str: Task ID.

        Example:
            >>> storage = TaskStorage("tasks.json")
            >>> from .models import Task
            >>> storage.add_task(Task("Plan"))
            ...
        """
        self.tasks[task.id] = task
        self.save()
        return task.id

    def get_task(self, task_id):
        """Fetch a task by ID.

        Args:
            task_id (str): Task ID.

        Returns:
            Task | None: The task if found, otherwise None.
        """
        return self.tasks.get(task_id)

    def update_task(self, task_id, **kwargs):
        """Update a task's fields and persist changes.

        Args:
            task_id (str): Task ID.
            **kwargs: Field-value pairs to update.

        Returns:
            bool: True when updated, False when not found.
        """
        task = self.get_task(task_id)
        if task:
            task.update(**kwargs)
            self.save()
            return True
        return False

    def delete_task(self, task_id):
        """Delete a task by ID.

        Args:
            task_id (str): Task ID.

        Returns:
            bool: True if deleted, False if not found.
        """
        if task_id in self.tasks:
            del self.tasks[task_id]
            self.save()
            return True
        return False

    def get_all_tasks(self):
        """Return all tasks currently in memory.

        Returns:
            list[Task]: All stored tasks.
        """
        return list(self.tasks.values())

    def get_tasks_by_status(self, status):
        """Filter tasks by status.

        Args:
            status (TaskStatus): Desired status.

        Returns:
            list[Task]: Tasks matching the status.
        """
        return [task for task in self.tasks.values() if task.status == status]

    def get_tasks_by_priority(self, priority):
        """Filter tasks by priority.

        Args:
            priority (TaskPriority): Desired priority.

        Returns:
            list[Task]: Tasks matching the priority.
        """
        return [task for task in self.tasks.values() if task.priority == priority]

    def get_overdue_tasks(self):
        """Return tasks that are overdue and not completed.

        Returns:
            list[Task]: Overdue tasks.
        """
        return [task for task in self.tasks.values() if task.is_overdue()]

