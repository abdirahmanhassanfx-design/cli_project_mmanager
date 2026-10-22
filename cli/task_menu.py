"""Task management screens."""

from rich.markup import escape

from cli.display import (
    detail_panel,
    format_due,
    names_by_id,
    print_error,
    print_hints,
    print_success,
    print_warning,
    project_names_by_id,
    styled,
    task_table,
)
from cli.prompts import ask_text, read_line
from cli.project_menu import ask_project, show_project_hints
from cli.screen import run_menu
from cli.user_menu import show_user_hints
from models.task import Task
from utils.exceptions import NotFoundError, ValidationError
from utils.validation import require_non_empty, validate_choice, validate_date


def run_task_menu(app) -> None:
    """Open the task management menu."""
    run_menu(
        app,
        "Task Management",
        [
            ("Create Task", create_task),
            ("List Tasks", list_tasks),
            ("View Task", view_task),
            ("Assign Contributor", assign_contributor),
            ("Mark Task Complete", mark_task_complete),
            ("Edit Task", edit_task),
            ("Back", None),
        ],
    )


def create_task(app) -> None:
    """Prompt for a task on an existing project."""
    if not show_project_hints(app):
        return
    project = ask_project(app)
    title = ask_text(
        app.console,
        "Task title",
        lambda value: require_non_empty(value, "Task title"),
    )
    description = ask_text(
        app.console,
        "Description",
        lambda value: require_non_empty(value, "Description"),
    )
    app.console.print("[dim]Priority: " + ", ".join(Task.VALID_PRIORITIES) + "[/dim]")
    priority = ask_text(
        app.console,
        "Priority",
        lambda value: validate_choice(value, Task.VALID_PRIORITIES, "priority"),
    )
    due_date = ask_text(app.console, "Due date", validate_date)
    task = app.tasks.create_task(project.id, title, description, priority, due_date)
    print_success(app.console, "Task created successfully.")
    app.console.print(f"Task ID: [bold cyan]{task.id}[/bold cyan]")


def list_tasks(app) -> None:
    """Show every task."""
    tasks = app.tasks.list_tasks()
    if not tasks:
        print_warning(app.console, "No tasks yet.")
        return
    app.console.print(
        task_table(tasks, project_names_by_id(app.projects.list_projects()))
    )


def view_task(app) -> None:
    """Show one task and the people contributing to it."""
    if not show_task_hints(app):
        return
    task = ask_task(app)
    names = names_by_id(app.users.list_users())
    project_name = project_names_by_id(app.projects.list_projects()).get(
        task.project_id,
        task.project_id,
    )
    app.console.print(
        detail_panel(
            task.title,
            [
                ("ID", escape(task.id)),
                ("Project", escape(project_name)),
                ("Description", escape(task.description)),
                ("Priority", styled(task.priority)),
                ("Status", styled(task.status)),
                ("Due date", format_due(task.due_date, task.status)),
                ("Created", escape(task.created_at)),
            ],
        )
    )
    _print_contributors(app, task, names)


def assign_contributor(app) -> None:
    """Assign one or more existing users to a task."""
    if not show_task_hints(app):
        return
    task = ask_task(app)
    if not show_user_hints(app):
        return
    app.console.print(
        "[dim]Enter a user ID to assign. Press Enter on an empty line when finished.[/dim]"
    )
    assigned = False
    while True:
        entered = read_line(app.console, "[bold]Contributor:[/bold] ")
        if entered == "":
            break
        try:
            user = app.users.find_user(entered)
            app.tasks.assign_contributor(task.id, user.id)
        except (ValidationError, NotFoundError) as exc:
            print_error(app.console, str(exc))
            continue
        print_success(app.console, f"Assigned {user.name} to '{task.title}'.")
        assigned = True
    if not assigned:
        print_warning(app.console, "No contributors were assigned.")


def mark_task_complete(app) -> None:
    """Mark one task as Completed."""
    if not show_task_hints(app):
        return
    task = ask_task(app)
    updated = app.tasks.mark_complete(task.id)
    print_success(
        app.console,
        f'Task {updated.id} "{updated.title}" marked as Completed.',
    )


def edit_task(app) -> None:
    """Edit a task's title, description, priority, due date, and status."""
    if not show_task_hints(app):
        return
    task = ask_task(app)
    app.console.print("[dim]Press Enter to keep the current value.[/dim]")
    app.console.print("[dim]Priority: " + ", ".join(Task.VALID_PRIORITIES) + "[/dim]")
    app.console.print("[dim]Status: " + ", ".join(Task.VALID_STATUSES) + "[/dim]")
    title = ask_text(
        app.console,
        "Task title",
        lambda value: require_non_empty(value, "Task title"),
        default=task.title,
    )
    description = ask_text(
        app.console,
        "Description",
        lambda value: require_non_empty(value, "Description"),
        default=task.description,
    )
    priority = ask_text(
        app.console,
        "Priority",
        lambda value: validate_choice(value, Task.VALID_PRIORITIES, "priority"),
        default=task.priority,
    )
    due_date = ask_text(app.console, "Due date", validate_date, default=task.due_date)
    status = ask_text(
        app.console,
        "Status",
        lambda value: validate_choice(value, Task.VALID_STATUSES, "task status"),
        default=task.status,
    )
    updated = app.tasks.update_task(
        task.id,
        title=title,
        description=description,
        priority=priority,
        due_date=due_date,
        status=status,
    )
    print_success(app.console, f"Task {updated.id} updated successfully.")


def ask_task(app):
    """Ask for a task ID until it matches an existing task."""
    return ask_text(app.console, "Task ID", app.tasks.find_task)


def show_task_hints(app) -> bool:
    """Print known tasks. Return False when there are none."""
    tasks = app.tasks.list_tasks()
    if not tasks:
        print_warning(app.console, "No tasks found. Create a task first.")
        return False
    print_hints(app.console, [(task.id, task.title) for task in tasks])
    return True


def _print_contributors(app, task, names: dict[str, str]) -> None:
    if not task.contributor_ids:
        print_warning(app.console, "No contributors assigned.")
        return
    app.console.print("[bold]Contributors[/bold]")
    for user_id in task.contributor_ids:
        app.console.print(f"  - {escape(names.get(user_id, user_id))}")
