FAQ — `storage.py`

Target audience: new/junior backend developers

Q1. What is the purpose of `storage.py`?
A1. `storage.py` implements the `TaskStorage` persistence layer for the app. It serializes `Task` objects to JSON and reads them back, providing methods to add, read, update, delete, and query tasks.

Q2. Where is the data stored by default?
A2. By default the storage file is `tasks.json` located in the current working directory. You can pass a different `storage_path` when creating `TaskStorage` or `TaskManager`.

Q3. How do I programmatically save a task?
A3. Use `TaskManager` or `TaskStorage`:

```python
from task_manager.app import TaskManager
mgr = TaskManager("data/tasks.json")
manager.create_task("Title", "desc", 2, "2026-02-20", ["tag1"])  # returns id

# OR direct storage
from task_manager.storage import TaskStorage
from task_manager.models import Task
s = TaskStorage("data/tasks.json")
t = Task("Do thing")
s.add_task(t)
```

Q4. What format is used for dates and datetimes?
A4. Dates and datetimes are serialized to ISO 8601 strings using `datetime.isoformat()` and parsed back with `datetime.fromisoformat()`.

Q5. What happens if the JSON file is corrupted?
A5. `TaskStorage.load()` catches exceptions and prints an error message like `Error loading tasks: <error>`. To recover, restore from backup or delete the corrupted file. The app will start with an empty store.

Q6. Does `TaskStorage` create missing directories for a custom path?
A6. No. If you pass `data/tasks.json` and `data/` doesn't exist, writing may raise `FileNotFoundError`. Create the directory first:

```bash
mkdir -p data
```

Q7. How are priorities and statuses stored?
A7. Enums from `models.py` are saved as their `.value` and reconstructed by `TaskDecoder`. Invalid enum values while decoding will raise `ValueError` in the decoder.

Q8. Why do I sometimes get `PermissionError`?
A8. The process needs permission to write the `storage_path`. Change to a writable location or adjust permissions.

Q9. Can I use a database instead of JSON?
A9. Yes—`TaskStorage` is a single implementation. To swap storage backends, implement the same API (`add_task`, `get_task`, `update_task`, `delete_task`, `get_all_tasks`, etc.) with a DB-backed class and update `TaskManager` to accept it.

Q10. What are the common mistakes new developers make?
A10.
- Running the CLI incorrectly (use `python -m task_manager.cli`).
- Using non-existent parent directories in `storage_path`.
- Manually editing `tasks.json` and introducing invalid JSON.
- Ignoring date format rules (use `YYYY-MM-DD`).

Q11. How do I debug save/load issues?
A11.
- Check printed errors when the app starts or when saving.
- Confirm the absolute path of `storage_path` (print `storage.storage_path`).
- Try loading the JSON with `python -c "import json; print(json.load(open('tasks.json')) )"` to surface decode errors.

If you'd like, I can expand this FAQ with an examples section showing sample corrupted JSON and recovery steps.
