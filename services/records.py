"""Load and save model objects in the JSON database."""

from models.project import Project
from models.task import Task
from models.user import User
from storage.json_storage import JsonStorage
from utils.exceptions import NotFoundError, StorageError
from utils.validation import normalize_id


def load_users(storage: JsonStorage) -> list[User]:
    """Return every user, or raise when a record is unreadable."""
    return [_build(User.from_dict, item, "user") for item in storage.data["users"]]


def load_projects(storage: JsonStorage) -> list[Project]:
    """Return every project, or raise when a record is unreadable."""
    return [
        _build(Project.from_dict, item, "project")
        for item in storage.data["projects"]
    ]


def load_tasks(storage: JsonStorage) -> list[Task]:
    """Return every task, or raise when a record is unreadable."""
    return [_build(Task.from_dict, item, "task") for item in storage.data["tasks"]]


def save_all(
    storage: JsonStorage,
    users: list[User] | None = None,
    projects: list[Project] | None = None,
    tasks: list[Task] | None = None,
) -> None:
    """Replace the given collections and write the database once."""
    if users is not None:
        storage.data["users"] = [user.to_dict() for user in users]
    if projects is not None:
        storage.data["projects"] = [project.to_dict() for project in projects]
    if tasks is not None:
        storage.data["tasks"] = [task.to_dict() for task in tasks]
    storage.save_data()


def require_user(storage: JsonStorage, user_id: str) -> User:
    """Return one user, or raise when the ID is unknown."""
    normalized = normalize_id(user_id, "User")
    for user in load_users(storage):
        if user.id == normalized:
            return user
    raise NotFoundError(f"No user found with ID {normalized}.")


def find_project(projects: list[Project], project_id: str) -> Project:
    """Find a project inside an already loaded list."""
    normalized = normalize_id(project_id, "Project")
    for project in projects:
        if project.id == normalized:
            return project
    raise NotFoundError(f"No project found with ID {normalized}.")


def find_task(tasks: list[Task], task_id: str) -> Task:
    """Find a task inside an already loaded list."""
    normalized = normalize_id(task_id, "Task")
    for task in tasks:
        if task.id == normalized:
            return task
    raise NotFoundError(f"No task found with ID {normalized}.")


def _build(factory, item: object, record_name: str):
    if not isinstance(item, dict):
        raise StorageError(f"Each {record_name} entry must be a JSON object.")
    try:
        return factory(item)
    except KeyError as exc:
        raise StorageError(
            f"A {record_name} record is missing required field {exc}."
        ) from exc
    except ValueError as exc:
        raise StorageError(f"A {record_name} record is invalid: {exc}") from exc
