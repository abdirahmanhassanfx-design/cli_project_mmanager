"""Project management screens."""

from rich import box
from rich.markup import escape
from rich.table import Table

from cli.display import (
    detail_panel,
    names_by_id,
    print_hints,
    print_success,
    print_warning,
    project_table,
    styled,
    task_table,
)
from cli.prompts import ask_text
from cli.screen import run_menu
from cli.user_menu import ask_user, show_user_hints
from models.project import Project
from utils.validation import require_non_empty, validate_choice


def run_project_menu(app) -> None:
    """Open the project management menu."""
    run_menu(
        app,
        "Project Management",
        [
            ("Create Project", create_project),
            ("List Projects", list_projects),
            ("View Project", view_project),
            ("Assign User to Project", assign_user),
            ("Search Projects", search_projects),
            ("Edit Project", edit_project),
            ("Back", None),
        ],
    )


def create_project(app) -> None:
    """Prompt for a project owned by an existing user."""
    if not show_user_hints(app):
        return
    app.console.print("[dim]Enter the project owner as a user ID.[/dim]")
    name = ask_text(
        app.console,
        "Project name",
        lambda value: require_non_empty(value, "Project name"),
    )
    description = ask_text(
        app.console,
        "Description",
        lambda value: require_non_empty(value, "Description"),
    )
    owner = ask_text(app.console, "Project owner", app.users.find_user)
    project = app.projects.create_project(name, description, owner.id)
    print_success(app.console, "Project created successfully.")
    app.console.print(f"Project ID: [bold cyan]{project.id}[/bold cyan]")


def list_projects(app) -> None:
    """Show every project."""
    projects = app.projects.list_projects()
    if not projects:
        print_warning(app.console, "No projects yet.")
        return
    app.console.print(project_table(projects, names_by_id(app.users.list_users())))


def view_project(app) -> None:
    """Show a project, its members, and its tasks."""
    if not show_project_hints(app):
        return
    project = ask_project(app)
    names = names_by_id(app.users.list_users())
    tasks = app.tasks.tasks_for_project(project.id)
    owner_name = names.get(project.owner_id, project.owner_id)
    done = sum(1 for task in tasks if task.is_complete())
    app.console.print(
        detail_panel(
            project.name,
            [
                ("ID", escape(project.id)),
                ("Description", escape(project.description)),
                ("Owner", escape(owner_name)),
                ("Status", styled(project.status)),
                ("Created", escape(project.created_at)),
                ("Tasks completed", f"{done} of {len(tasks)}"),
            ],
        )
    )
    _print_members(app, project, names)
    if tasks:
        app.console.print(task_table(tasks, {project.id: project.name}))
    else:
        print_warning(app.console, "This project has no tasks yet.")


def assign_user(app) -> None:
    """Add an existing user to a project."""
    if not show_project_hints(app):
        return
    project = ask_project(app)
    if not show_user_hints(app):
        return
    user = ask_user(app)
    app.projects.assign_user(project.id, user.id)
    print_success(app.console, f"Assigned {user.name} to {project.name}.")


def search_projects(app) -> None:
    """Search projects by ID, name, owner, or status."""
    query = ask_text(
        app.console,
        "Search projects",
        lambda value: require_non_empty(value, "Search"),
    )
    matches = app.projects.search_projects(query)
    if not matches:
        print_warning(app.console, f"No projects matched '{query}'.")
        return
    app.console.print(project_table(matches, names_by_id(app.users.list_users())))


def edit_project(app) -> None:
    """Edit a project's name, description, and status."""
    if not show_project_hints(app):
        return
    project = ask_project(app)
    app.console.print("[dim]Press Enter to keep the current value.[/dim]")
    app.console.print("[dim]Status: " + ", ".join(Project.VALID_STATUSES) + "[/dim]")
    name = ask_text(
        app.console,
        "Project name",
        lambda value: require_non_empty(value, "Project name"),
        default=project.name,
    )
    description = ask_text(
        app.console,
        "Description",
        lambda value: require_non_empty(value, "Description"),
        default=project.description,
    )
    status = ask_text(
        app.console,
        "Status",
        lambda value: validate_choice(value, Project.VALID_STATUSES, "project status"),
        default=project.status,
    )
    updated = app.projects.update_project(
        project.id,
        name=name,
        description=description,
        status=status,
    )
    print_success(app.console, f"Project {updated.id} updated successfully.")


def ask_project(app):
    """Ask for a project ID until it matches an existing project."""
    return ask_text(app.console, "Project", app.projects.find_project)


def show_project_hints(app) -> bool:
    """Print known projects. Return False when there are none."""
    projects = app.projects.list_projects()
    if not projects:
        print_warning(app.console, "No projects found. Create a project first.")
        return False
    print_hints(app.console, [(project.id, project.name) for project in projects])
    return True


def _print_members(app, project, names: dict[str, str]) -> None:
    table = Table(title="Members", box=box.ROUNDED, header_style="bold cyan")
    table.add_column("ID", style="cyan")
    table.add_column("Name")
    table.add_column("Relationship")
    for member_id in project.member_ids:
        relationship = "Owner" if member_id == project.owner_id else "Member"
        table.add_row(
            escape(member_id),
            escape(names.get(member_id, member_id)),
            relationship,
        )
    app.console.print(table)
