"""Command-line interface for the task manager application."""

# task_manager/cli.py
import argparse
from datetime import datetime
from .app import TaskManager
from .models import TaskPriority, TaskStatus

def format_task(task):
    """Render a task as a human-readable multi-line string.

    Args:
        task (Task): Task instance to format.

    Returns:
        str: Human-friendly string representation for CLI output.

    Raises:
        AttributeError: If `task` is missing expected attributes.

    Example:
        >>> from .models import Task
        >>> t = Task("Write tests")
        >>> isinstance(format_task(t), str)
        True

    Notes:
        Uses compact status and priority symbols for quick scanning.
    """
    status_symbol = {
        TaskStatus.TODO: "[ ]",
        TaskStatus.IN_PROGRESS: "[>]",
        TaskStatus.REVIEW: "[?]",
        TaskStatus.DONE: "[✓]",
        TaskStatus.ABANDONED: "[x]"
    }

    priority_symbol = {
        TaskPriority.LOW: "!",
        TaskPriority.MEDIUM: "!!",
        TaskPriority.HIGH: "!!!",
        TaskPriority.URGENT: "!!!!"
    }

    due_str = f"Due: {task.due_date.strftime('%Y-%m-%d')}" if task.due_date else "No due date"
    tags_str = f"Tags: {', '.join(task.tags)}" if task.tags else "No tags"

    return (
        f"{status_symbol[task.status]} {task.id[:8]} - {priority_symbol[task.priority]} {task.title}\n"
        f"  {task.description}\n"
        f"  {due_str} | {tags_str}\n"
        f"  Created: {task.created_at.strftime('%Y-%m-%d %H:%M')}"
    )

def main():
    """Entry point for the CLI.

    Returns:
        None

    Raises:
        SystemExit: Raised by argparse on invalid arguments.

    Example:
        >>> # python -m task_manager.cli list
        ...

    Notes:
        This function wires command parsing to `TaskManager` operations.
    """
    parser = argparse.ArgumentParser(description="Task Manager CLI")
    subparsers = parser.add_subparsers(dest="command", help="Command to execute")

    # Create task command
    create_parser = subparsers.add_parser("create", help="Create a new task")
    create_parser.add_argument("title", help="Task title")
    create_parser.add_argument("-d", "--description", help="Task description", default="")
    create_parser.add_argument("-p", "--priority", help="Task priority (1-4)", type=int, choices=[1, 2, 3, 4], default=2)
    create_parser.add_argument("-u", "--due", help="Due date (YYYY-MM-DD)", default=None)
    create_parser.add_argument("-t", "--tags", help="Comma-separated tags", default="")

    # List tasks command
    list_parser = subparsers.add_parser("list", help="List all tasks")
    list_parser.add_argument("-s", "--status", help="Filter by status", choices=["todo", "in_progress", "review", "done", "abandoned"])
    list_parser.add_argument("-p", "--priority", help="Filter by priority", type=int, choices=[1, 2, 3, 4])
    list_parser.add_argument("-o", "--overdue", help="Show only overdue tasks", action="store_true")

    # Update task commands
    update_status_parser = subparsers.add_parser("status", help="Update task status")
    update_status_parser.add_argument("task_id", help="Task ID")
    update_status_parser.add_argument("status", help="New status", choices=["todo", "in_progress", "review", "done", "abandoned"])

    update_priority_parser = subparsers.add_parser("priority", help="Update task priority")
    update_priority_parser.add_argument("task_id", help="Task ID")
    update_priority_parser.add_argument("priority", help="New priority", type=int, choices=[1, 2, 3, 4])

    update_due_parser = subparsers.add_parser("due", help="Update task due date")
    update_due_parser.add_argument("task_id", help="Task ID")
    update_due_parser.add_argument("due_date", help="New due date (YYYY-MM-DD)")

    # Tag management
    add_tag_parser = subparsers.add_parser("tag", help="Add tag to task")
    add_tag_parser.add_argument("task_id", help="Task ID")
    add_tag_parser.add_argument("tag", help="Tag to add")

    remove_tag_parser = subparsers.add_parser("untag", help="Remove tag from task")
    remove_tag_parser.add_argument("task_id", help="Task ID")
    remove_tag_parser.add_argument("tag", help="Tag to remove")

    # Other commands
    show_parser = subparsers.add_parser("show", help="Show task details")
    show_parser.add_argument("task_id", help="Task ID")

    delete_parser = subparsers.add_parser("delete", help="Delete a task")
    delete_parser.add_argument("task_id", help="Task ID")

    stats_parser = subparsers.add_parser("stats", help="Show task statistics")

    args = parser.parse_args()
    task_manager = TaskManager()

    def handle_create():
        tags = [tag.strip() for tag in args.tags.split(",")] if args.tags else []
        task_id = task_manager.create_task(
            args.title,
            args.description,
            args.priority,
            args.due,
            tags
        )
        if task_id:
            print(f"Created task with ID: {task_id}")

    def handle_list():
        tasks = task_manager.list_tasks(args.status, args.priority, args.overdue)
        if tasks:
            for task in tasks:
                print(format_task(task))
                print("-" * 50)
        else:
            print("No tasks found matching the criteria.")

    def handle_status():
        if task_manager.update_task_status(args.task_id, args.status):
            print(f"Updated task status to {args.status}")
        else:
            print("Failed to update task status. Task not found.")

    def handle_priority():
        if task_manager.update_task_priority(args.task_id, args.priority):
            print(f"Updated task priority to {args.priority}")
        else:
            print("Failed to update task priority. Task not found.")

    def handle_due():
        if task_manager.update_task_due_date(args.task_id, args.due_date):
            print(f"Updated task due date to {args.due_date}")
        else:
            print("Failed to update task due date. Task not found or invalid date.")

    def handle_tag():
        if task_manager.add_tag_to_task(args.task_id, args.tag):
            print(f"Added tag '{args.tag}' to task")
        else:
            print("Failed to add tag. Task not found.")

    def handle_untag():
        if task_manager.remove_tag_from_task(args.task_id, args.tag):
            print(f"Removed tag '{args.tag}' from task")
        else:
            print("Failed to remove tag. Task or tag not found.")

    def handle_show():
        task = task_manager.get_task_details(args.task_id)
        if task:
            print(format_task(task))
        else:
            print("Task not found.")

    def handle_delete():
        if task_manager.delete_task(args.task_id):
            print(f"Deleted task {args.task_id}")
        else:
            print("Failed to delete task. Task not found.")

    def handle_stats():
        stats = task_manager.get_statistics()
        print(f"Total tasks: {stats['total']}")
        print("By status:")
        for status, count in stats['by_status'].items():
            print(f"  {status}: {count}")
        print("By priority:")
        for priority, count in stats['by_priority'].items():
            print(f"  {priority}: {count}")
        print(f"Overdue tasks: {stats['overdue']}")
        print(f"Completed in last 7 days: {stats['completed_last_week']}")

    handlers = {
        "create": handle_create,
        "list": handle_list,
        "status": handle_status,
        "priority": handle_priority,
        "due": handle_due,
        "tag": handle_tag,
        "untag": handle_untag,
        "show": handle_show,
        "delete": handle_delete,
        "stats": handle_stats,
    }

    handler = handlers.get(args.command)
    if handler:
        handler()
    else:
        parser.print_help()

if __name__ == "__main__":
    main()