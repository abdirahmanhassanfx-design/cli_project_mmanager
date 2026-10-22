"""Open the database and wire the services together."""

from pathlib import Path

from services.project_service import ProjectService
from services.records import load_projects, load_tasks, load_users
from services.report_service import ReportService
from services.seed import seed_sample_data
from services.task_service import TaskService
from services.user_service import UserService
from storage.json_storage import JsonStorage


def open_tracker(db_path: str | Path, seed_if_new: bool = True):
    """Load storage and services.

    Sample data is inserted only when this process creates the database file.
    An existing file, including one an administrator has edited, is left as it is.
    """
    storage = JsonStorage(db_path)
    if not storage.created_new:
        load_users(storage)
        load_projects(storage)
        load_tasks(storage)

    users = UserService(storage)
    projects = ProjectService(storage)
    tasks = TaskService(storage)
    reports = ReportService(storage)
    if seed_if_new and storage.created_new:
        seed_sample_data(users, projects, tasks)
    return storage, users, projects, tasks, reports
