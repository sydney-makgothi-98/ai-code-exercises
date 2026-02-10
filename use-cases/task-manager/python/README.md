# Task Manager

A simple CLI tool that helps backend developers quickly track the progress of a task.

## Description

Task Manager is a lightweight command-line application for creating, listing, updating, and persisting task objects. It focuses on quick workflow for backend devs who want to track task status, priority, tags, and due dates using a local JSON-backed storage.

## Technologies

- Python 3.10+
- Standard library: `argparse`, `json`, `datetime`, `os`
- Project modules: `app.py`, `cli.py`, `storage.py`, `models.py`

## Installation Requirements

- Python 3.10 or newer
- (Optional) Create and activate a virtual environment

Commands:

```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS / Linux
source .venv/bin/activate
```

Install any additional dependencies (if you add them later):

```bash
pip install -r requirements.txt
```

## Running the CLI

Run the CLI from the project root (module context is required since code uses relative imports):

```bash
python -m task_manager.cli <command> [options]
```

Examples:

```bash
# Create a task
python -m task_manager.cli create "Write docs" -d "Add README and FAQ" -p 2 -u 2026-02-14 -t docs,writing

# List all tasks
python -m task_manager.cli list

# Show a task
python -m task_manager.cli show <task_id>

# Update status
python -m task_manager.cli status <task_id> done

# Delete
python -m task_manager.cli delete <task_id>
```

## Features Overview

- Create, read, update, delete (CRUD) tasks via CLI
- Filter tasks by status or priority
- Mark tasks done, set due dates, and manage tags
- JSON-backed persistence through `TaskStorage` (see `storage.py`)
- Automatic stale-task handling in `TaskManager`

## Configuration

- Default storage file: `tasks.json` in the current working directory.
- You may pass a custom storage path when instantiating `TaskManager` or `TaskStorage`.

Example (programmatic):

```python
from task_manager.app import TaskManager
manager = TaskManager(storage_path="data/my_tasks.json")
```

## Storage details

`TaskStorage` (see [storage.py](storage.py)) uses JSON serialization to persist tasks. By default it loads from and saves to `tasks.json`. You can supply a full path to place the file elsewhere (e.g., `data/tasks.json`).

Common storage patterns:

```python
from task_manager.storage import TaskStorage
from task_manager.models import Task, TaskPriority

storage = TaskStorage("data/tasks.json")
# Create a Task via Task model and add
new = Task("Title")
storage.add_task(new)
```

Or via the app facade:

```python
from task_manager.app import TaskManager
mgr = TaskManager("data/tasks.json")
mgr.create_task("Title", "desc", 2, "2026-02-14", ["tag1"])  # returns task_id
```

## Troubleshooting

- JSON decode / corrupt file: delete or move the corrupted `tasks.json` and restart.
- Permission errors: ensure the process can read/write the storage path and parent directory.
- Invalid dates: use `YYYY-MM-DD` format for due dates.
- Relative imports errors: run CLI using module form (`python -m task_manager.cli`) from the repository root.

## Contributing

- Fork the repo, create a feature branch, and open a pull request.
- Keep changes focused and add tests where appropriate.
- Follow PEP8 and include docstrings for new modules/functions.

## License

This project is available under the MIT License. See LICENSE for details.

## Files

- [app.py](app.py) - application facade (`TaskManager`)
- [cli.py](cli.py) - command-line entrypoint and argument parsing
- [storage.py](storage.py) - JSON-backed persistence (`TaskStorage`)
- [models.py](models.py) - `Task`, `TaskPriority`, `TaskStatus`
- [algo.py](algo.py) - (utility / algorithms)
- [product_API.py](product_API.py) - (API sketch)
- [Documentation.md](Documentation.md) - other docs

If you'd like I can also add a `requirements.txt` and LICENSE file.
