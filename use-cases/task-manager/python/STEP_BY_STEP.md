Step-by-step Guide: Storing Data with Task Manager

Prerequisites

1. Python 3.10+ installed.
2. Project checked out locally.
3. Optional: virtual environment activated.
4. File system write access to the folder where you want to persist tasks.

Goal

Store a new task so it is persisted to disk and accessible from the CLI and programmatic APIs.

Steps

1. Open a Python REPL or script from the project root.

2. Choose whether to use the `TaskManager` facade (recommended) or `TaskStorage` directly.

3. Examples (use the `task_manager` package import path):

Programmatic: using `TaskManager` (recommended)

```python
from task_manager.app import TaskManager

# Use a custom path or default "tasks.json" in cwd
manager = TaskManager(storage_path="data/tasks.json")

# Create a new task
task_id = manager.create_task(
    "Write integration tests",
    description="Cover edge cases for storage",
    priority_value=2,
    due_date_str="2026-02-20",
    tags=["tests", "storage"]
)
print("Created", task_id)
```

Direct storage usage: using `TaskStorage`

```python
from task_manager.storage import TaskStorage
from task_manager.models import Task, TaskPriority

storage = TaskStorage(storage_path="data/tasks.json")

# Construct a Task object and add
task = Task("Refactor storage code")
# Optionally set fields
# task.description = "..."
# task.priority = TaskPriority(3)

task_id = storage.add_task(task)
print("Saved task id:", task_id)
```

Where to put the file

- By default `TaskStorage` uses `tasks.json` in the current working directory.
- Provide a path to `TaskManager`/`TaskStorage` to use a different folder, e.g., `data/tasks.json`.
- Ensure the parent directory exists (the library does not create nested directories for you).

Screenshots / Code Path (storage method reference)

Open [storage.py](storage.py) and look at the `TaskStorage` constructor and methods:

```python
class TaskStorage:
    def __init__(self, storage_path="tasks.json"):
        self.storage_path = storage_path
        self.tasks = {}
        self.load()

    def add_task(self, task):
        self.tasks[task.id] = task
        self.save()
        return task.id
```

Potential issues / common mistakes

- Not creating parent directories for a custom `storage_path` causes a `FileNotFoundError` when writing. Create the directory first:

```bash
mkdir -p data
```

- Using a non-writable location (e.g., system root) will fail with permission errors.
- Corrupting `tasks.json` (manual edits) can lead to load failures; back up the file or remove it to reset.
- Running `cli.py` directly can raise import errors due to relative imports—use module run form: `python -m task_manager.cli`.

Troubleshooting

- "Error loading tasks: <message>" — the file is missing, unreadable, or contains invalid JSON. Move or delete the file and re-run.
- "Permission denied" — change storage path or file permissions.
- No tasks appear — confirm that you're pointing to the same `tasks.json` the CLI is using; check absolute paths if needed.

Advanced

- For test isolation, use a temporary file for storage:

```python
import tempfile
from task_manager.app import TaskManager

fd, path = tempfile.mkstemp(prefix="tasks_", suffix=".json")
manager = TaskManager(storage_path=path)
# run tests...
```

End of guide.
