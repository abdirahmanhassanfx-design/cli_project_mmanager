"""Cross-cutting search screens."""

from rich.markup import escape

from cli.project_menu import search_projects
from cli.screen import run_menu
from cli.user_menu import ask_user, search_users, show_user_hints
from cli.display import print_warning


def run_search_menu(app) -> None:
    """Open search for users, projects, and a user's assignments."""
    run_menu(
        app,
        "Search",
        [
            ("Search Users", search_users),
            ("Search Projects", search_projects),
            ("Projects for a User", projects_for_user),
            ("Back", None),
        ],
    )


def projects_for_user(app) -> None:
    """List every project owned by or assigned to one user."""
    if not show_user_hints(app):
        return
    user = ask_user(app)
    projects = app.projects.projects_for_user(user.id)
    app.console.print()
    app.console.print(f"[bold]Projects assigned to {escape(user.name)}:[/bold]")
    app.console.print()
    if not projects:
        print_warning(app.console, "This user is not assigned to any projects.")
        return
    for project in projects:
        app.console.print(
            f"[cyan]{escape(project.id)}[/cyan] - {escape(project.name)}"
        )
