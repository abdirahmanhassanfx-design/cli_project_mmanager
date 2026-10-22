"""User management screens."""

from rich.markup import escape

from cli.display import (
    detail_panel,
    names_by_id,
    print_error,
    print_hints,
    print_success,
    print_warning,
    project_names_by_id,
    project_table,
    task_table,
    user_table,
)
from cli.prompts import ask_text
from cli.screen import run_menu
from utils.exceptions import ValidationError
from utils.validation import require_non_empty, validate_email


def run_user_menu(app) -> None:
    """Open the user management menu."""
    run_menu(
        app,
        "User Management",
        [
            ("Create User", create_user),
            ("List Users", list_users),
            ("Search Users", search_users),
            ("View User", view_user),
            ("Edit User", edit_user),
            ("Back", None),
        ],
    )


def create_user(app) -> None:
    """Prompt for a new user and save them."""
    name = ask_text(app.console, "Name", lambda value: require_non_empty(value, "Name"))
    email = ask_text(app.console, "Email", lambda value: _new_email(app, value))
    role = ask_text(app.console, "Role", lambda value: require_non_empty(value, "Role"))
    user = app.users.create_user(name, email, role)
    print_success(app.console, "User created successfully.")
    app.console.print(f"User ID: [bold cyan]{user.id}[/bold cyan]")


def list_users(app) -> None:
    """Show every user."""
    users = app.users.list_users()
    if not users:
        print_warning(app.console, "No users yet.")
        return
    app.console.print(user_table(users))


def search_users(app) -> None:
    """Search users by name, email, or ID."""
    query = ask_text(
        app.console,
        "Search by name, email, or ID",
        lambda value: require_non_empty(value, "Search"),
    )
    matches = app.users.search_users(query)
    if not matches:
        print_warning(app.console, f"No users matched '{query}'.")
        return
    app.console.print(user_table(matches))


def view_user(app) -> None:
    """Show one user plus their projects and task contributions."""
    if not show_user_hints(app):
        return
    user = ask_user(app)
    projects = app.projects.projects_for_user(user.id)
    tasks = app.tasks.tasks_for_user(user.id)
    app.console.print(
        detail_panel(
            user.name,
            [
                ("ID", escape(user.id)),
                ("Email", escape(user.email)),
                ("Role", escape(user.role)),
            ],
        )
    )
    if projects:
        app.console.print(project_table(projects, names_by_id(app.users.list_users())))
    else:
        print_warning(app.console, "This user is not assigned to any projects.")
    if tasks:
        app.console.print(
            task_table(tasks, project_names_by_id(app.projects.list_projects()))
        )
    else:
        print_warning(app.console, "This user is not a contributor on any tasks.")


def edit_user(app) -> None:
    """Edit a user's name, email, and role."""
    if not show_user_hints(app):
        return
    user = ask_user(app)
    app.console.print("[dim]Press Enter to keep the current value.[/dim]")
    name = ask_text(
        app.console,
        "Name",
        lambda value: require_non_empty(value, "Name"),
        default=user.name,
    )
    email = ask_text(
        app.console,
        "Email",
        lambda value: _new_email(app, value, ignore_id=user.id),
        default=user.email,
    )
    role = ask_text(
        app.console,
        "Role",
        lambda value: require_non_empty(value, "Role"),
        default=user.role,
    )
    updated = app.users.update_user(user.id, name=name, email=email, role=role)
    print_success(app.console, f"User {updated.id} updated successfully.")


def ask_user(app):
    """Ask for a user ID until it matches an existing user."""
    return ask_text(app.console, "User ID", app.users.find_user)


def show_user_hints(app) -> bool:
    """Print known users. Return False when there are none."""
    users = app.users.list_users()
    if not users:
        print_error(app.console, "No users found. Create a user first.")
        return False
    print_hints(app.console, [(user.id, user.name) for user in users])
    return True


def _new_email(app, value: str, ignore_id: str | None = None) -> str:
    email = validate_email(value)
    for user in app.users.list_users():
        if user.id == ignore_id:
            continue
        if user.email.casefold() == email.casefold():
            raise ValidationError(f"A user with email {email} already exists.")
    return email
