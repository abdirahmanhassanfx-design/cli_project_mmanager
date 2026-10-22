"""Main menu and application startup."""

from pathlib import Path

from rich.markup import escape
from rich.panel import Panel

from cli.display import make_console, print_error, print_success, show_banner, show_menu
from cli.project_menu import run_project_menu
from cli.prompts import ask_menu_choice, pause
from cli.report_menu import run_report_menu
from cli.search_menu import run_search_menu
from cli.task_menu import run_task_menu
from cli.user_menu import run_user_menu
from utils.exceptions import NotFoundError, StorageError, ValidationError


class Application:
    """Terminal front end. Menus call services and never touch the JSON file."""

    def __init__(
        self,
        users,
        projects,
        tasks,
        reports,
        database_path: Path,
        seeded: bool,
    ) -> None:
        self.users = users
        self.projects = projects
        self.tasks = tasks
        self.reports = reports
        self.database_path = database_path
        self.seeded = seeded
        self.console = make_console()

    def run(self) -> None:
        """Stay in the main menu until the administrator exits."""
        try:
            if self.seeded:
                print_success(
                    self.console,
                    "Sample data loaded so you can explore the system.",
                )
            self._main_loop()
        except (KeyboardInterrupt, EOFError):
            self.console.print("\n[cyan]Goodbye.[/cyan]")

    def _main_loop(self) -> None:
        actions = {
            "1": run_user_menu,
            "2": run_project_menu,
            "3": run_task_menu,
            "4": run_search_menu,
            "5": run_report_menu,
        }
        while True:
            show_banner(self.console)
            show_menu(
                self.console,
                "Main Menu",
                [
                    "User Management",
                    "Project Management",
                    "Task Management",
                    "Search",
                    "Reports",
                    "Exit",
                ],
            )
            self.console.print(
                f"[dim]Changes are saved automatically to {escape(str(self.database_path))}[/dim]"
            )
            choice = ask_menu_choice(self.console, 6)
            if choice == "6":
                self.console.print(Panel.fit("Goodbye.", border_style="cyan"))
                return
            try:
                actions[choice](self)
            except (ValidationError, NotFoundError, StorageError, ValueError, KeyError) as exc:
                print_error(self.console, str(exc))
                pause(self.console)
