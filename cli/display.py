"""Shared Rich output for menus, tables, and messages."""

from datetime import date, datetime

from rich import box
from rich.console import Console
from rich.markup import escape
from rich.panel import Panel
from rich.table import Table

from models.project import Project
from models.task import Task
from models.user import User

STATUS_STYLES = {
    "Planning": "yellow",
    "Active": "green",
    "Completed": "blue",
    "Archived": "bright_black",
    "Pending": "yellow",
    "In Progress": "cyan",
    "Low": "green",
    "Medium": "yellow",
    "High": "red",
    "Critical": "bold red",
}


def make_console() -> Console:
    """Return a console that does not auto-highlight user data."""
    return Console(highlight=False)


def show_banner(console: Console) -> None:
    """Print the application title."""
    console.print()
    console.print(
        Panel.fit(
            "[bold]PROJECT MANAGEMENT SYSTEM[/bold]",
            border_style="cyan",
            padding=(1, 4),
        )
    )


def show_menu(console: Console, title: str, options: list[str]) -> None:
    """Print a numbered menu inside a panel."""
    lines = [
        f"[bold cyan]{index}.[/bold cyan] {escape(label)}"
        for index, label in enumerate(options, start=1)
    ]
    console.print()
    console.print(
        Panel("\n".join(lines), title=escape(title), border_style="cyan", padding=(1, 2))
    )


def print_success(console: Console, message: str) -> None:
    """Print a green confirmation."""
    console.print(f"[bold green]{escape(message)}[/bold green]")


def print_error(console: Console, message: str) -> None:
    """Print a red explanation."""
    console.print(f"[bold red]{escape(message)}[/bold red]")


def print_warning(console: Console, message: str) -> None:
    """Print a yellow notice."""
    console.print(f"[bold yellow]{escape(message)}[/bold yellow]")


def styled(value: str) -> str:
    """Color a known status or priority."""
    style = STATUS_STYLES.get(value, "white")
    return f"[{style}]{escape(value)}[/{style}]"


def detail_panel(title: str, rows: list[tuple[str, str]]) -> Panel:
    """Build a two-column details panel.

    Values may already contain Rich markup. Labels are escaped.
    """
    table = Table(show_header=False, box=box.SIMPLE, pad_edge=False)
    table.add_column(style="bold cyan", no_wrap=True)
    table.add_column(overflow="fold")
    for label, value in rows:
        table.add_row(escape(label), value)
    return Panel(table, title=escape(title), border_style="cyan")


def user_table(users: list[User]) -> Table:
    """Build the user listing table."""
    table = Table(title="Users", box=box.ROUNDED, header_style="bold cyan")
    table.add_column("ID", style="cyan", no_wrap=True)
    table.add_column("Name")
    table.add_column("Email")
    table.add_column("Role")
    for user in users:
        table.add_row(
            escape(user.id),
            escape(user.name),
            escape(user.email),
            escape(user.role),
        )
    return table


def project_table(projects: list[Project], owner_names: dict[str, str]) -> Table:
    """Build the project listing table."""
    table = Table(title="Projects", box=box.ROUNDED, header_style="bold cyan")
    table.add_column("ID", style="cyan", no_wrap=True)
    table.add_column("Project")
    table.add_column("Owner")
    table.add_column("Status")
    for project in projects:
        owner = owner_names.get(project.owner_id, project.owner_id)
        table.add_row(
            escape(project.id),
            escape(project.name),
            escape(owner),
            styled(project.status),
        )
    return table


def task_table(tasks: list[Task], project_names: dict[str, str]) -> Table:
    """Build the task listing table."""
    table = Table(title="Tasks", box=box.ROUNDED, header_style="bold cyan")
    table.add_column("ID", style="cyan", no_wrap=True)
    table.add_column("Title")
    table.add_column("Project")
    table.add_column("Priority")
    table.add_column("Status")
    table.add_column("Due")
    for task in tasks:
        project_name = project_names.get(task.project_id, task.project_id)
        table.add_row(
            escape(task.id),
            escape(task.title),
            escape(project_name),
            styled(task.priority),
            styled(task.status),
            format_due(task.due_date, task.status),
        )
    return table


def format_due(due_date: str, status: str) -> str:
    """Highlight a due date when the task is still open and past due."""
    try:
        due = datetime.strptime(due_date, "%Y-%m-%d").date()
    except ValueError:
        return escape(due_date)
    if status != "Completed" and due < date.today():
        return f"[red]{escape(due_date)} (overdue)[/red]"
    return escape(due_date)


def print_hints(console: Console, pairs: list[tuple[str, str]]) -> None:
    """Print a one-line index of IDs and labels."""
    hints = ", ".join(
        f"{escape(identifier)} ({escape(label)})" for identifier, label in pairs
    )
    console.print(f"[dim]{hints}[/dim]")


def names_by_id(users: list[User]) -> dict[str, str]:
    """Map user IDs to display names."""
    return {user.id: user.name for user in users}


def project_names_by_id(projects: list[Project]) -> dict[str, str]:
    """Map project IDs to display names."""
    return {project.id: project.name for project in projects}
