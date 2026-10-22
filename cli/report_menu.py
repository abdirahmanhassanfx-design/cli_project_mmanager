"""Summary reports."""

from rich import box
from rich.markup import escape
from rich.table import Table

from cli.display import print_warning
from cli.screen import run_menu


def run_report_menu(app) -> None:
    """Open the reports menu."""
    run_menu(
        app,
        "Reports",
        [
            ("Project Summary", project_summary),
            ("Task Summary", task_summary),
            ("User Workload", user_workload),
            ("Back", None),
        ],
    )


def project_summary(app) -> None:
    """Show how many projects are in each status."""
    summary = app.reports.project_summary()
    app.console.print(
        _count_table(
            "Project Summary",
            [
                ("Total Projects", summary["total"]),
                ("Planning", summary["Planning"]),
                ("Active Projects", summary["Active"]),
                ("Completed Projects", summary["Completed"]),
                ("Archived Projects", summary["Archived"]),
            ],
        )
    )


def task_summary(app) -> None:
    """Show how many tasks are in each status."""
    summary = app.reports.task_summary()
    app.console.print(
        _count_table(
            "Task Summary",
            [
                ("Total Tasks", summary["total"]),
                ("Pending", summary["Pending"]),
                ("In Progress", summary["In Progress"]),
                ("Completed", summary["Completed"]),
            ],
        )
    )


def user_workload(app) -> None:
    """Show how many projects and tasks are linked to each user."""
    rows = app.reports.user_workload()
    if not rows:
        print_warning(app.console, "No users yet.")
        return
    table = Table(title="User Workload", box=box.ROUNDED, header_style="bold cyan")
    table.add_column("User")
    table.add_column("Projects", justify="right")
    table.add_column("Tasks", justify="right")
    for row in rows:
        table.add_row(escape(str(row["name"])), str(row["projects"]), str(row["tasks"]))
    app.console.print(table)


def _count_table(title: str, rows: list[tuple[str, int]]) -> Table:
    table = Table(title=title, box=box.ROUNDED, header_style="bold cyan")
    table.add_column("Metric")
    table.add_column("Count", justify="right")
    for label, count in rows:
        table.add_row(label, str(count))
    return table
