"""Create, assign, update, and complete tasks."""

from datetime import datetime

from models.task import Task
from services.records import (
    find_project,
    find_task,
    load_projects,
    load_tasks,
    require_user,
    save_all,
)
from storage.json_storage import JsonStorage
from utils.exceptions import ValidationError
from utils.ids import next_id
from utils.validation import require_non_empty, validate_choice, validate_date


class TaskService:
    """Business rules for tasks and their contributors."""

    def __init__(self, storage: JsonStorage) -> None:
        self.storage = storage

    def create_task(
        self,
        project_id: str,
        title: str,
        description: str,
        priority: str,
        due_date: str,
        contributor_ids: list[str] | None = None,
    ) -> Task:
        """Create a task on an existing project and save both records.

        Contributor IDs are optional here. Administrators can assign people
        later. Every supplied contributor must already exist.
        """
        cleaned_title = require_non_empty(title, "Task title")
        cleaned_description = require_non_empty(description, "Description")
        cleaned_priority = validate_choice(priority, Task.VALID_PRIORITIES, "priority")
        cleaned_due = validate_date(due_date)

        projects = load_projects(self.storage)
        project = find_project(projects, project_id)
        contributor_ids = self._collect_contributors(contributor_ids or [])
        tasks = load_tasks(self.storage)
        task = Task(
            id=next_id([item.id for item in tasks], "T"),
            title=cleaned_title,
            description=cleaned_description,
            project_id=project.id,
            contributor_ids=contributor_ids,
            status="Pending",
            priority=cleaned_priority,
            due_date=cleaned_due,
            created_at=_timestamp(),
        )
        project.add_task(task.id)
        tasks.append(task)
        save_all(self.storage, projects=projects, tasks=tasks)
        return task

    def list_tasks(self) -> list[Task]:
        """Return tasks ordered by ID."""
        return sorted(load_tasks(self.storage), key=lambda task: task.id)

    def find_task(self, task_id: str) -> Task:
        """Return the task with this ID."""
        return find_task(self.list_tasks(), task_id)

    def tasks_for_project(self, project_id: str) -> list[Task]:
        """Return the tasks that belong to one project."""
        project = find_project(load_projects(self.storage), project_id)
        return [task for task in self.list_tasks() if task.project_id == project.id]

    def tasks_for_user(self, user_id: str) -> list[Task]:
        """Return tasks that list the user as a contributor."""
        user = require_user(self.storage, user_id)
        return [
            task for task in self.list_tasks() if user.id in task.contributor_ids
        ]

    def assign_contributor(self, task_id: str, user_id: str) -> Task:
        """Add one existing user as a task contributor."""
        tasks = load_tasks(self.storage)
        task = find_task(tasks, task_id)
        user = require_user(self.storage, user_id)
        if not task.assign_contributor(user.id):
            raise ValidationError(
                f"{user.name} is already a contributor on '{task.title}'."
            )
        save_all(self.storage, tasks=tasks)
        return task

    def mark_complete(self, task_id: str) -> Task:
        """Set a task to Completed and save."""
        tasks = load_tasks(self.storage)
        task = find_task(tasks, task_id)
        task.mark_complete()
        save_all(self.storage, tasks=tasks)
        return task

    def update_task(
        self,
        task_id: str,
        title: str | None = None,
        description: str | None = None,
        priority: str | None = None,
        due_date: str | None = None,
        status: str | None = None,
    ) -> Task:
        """Change editable task fields and save immediately."""
        tasks = load_tasks(self.storage)
        task = find_task(tasks, task_id)
        cleaned_title = require_non_empty(title, "Task title") if title is not None else None
        cleaned_description = (
            require_non_empty(description, "Description") if description is not None else None
        )
        cleaned_priority = (
            validate_choice(priority, Task.VALID_PRIORITIES, "priority")
            if priority is not None
            else None
        )
        cleaned_due = validate_date(due_date) if due_date is not None else None
        cleaned_status = (
            validate_choice(status, Task.VALID_STATUSES, "task status")
            if status is not None
            else None
        )
        task.update(
            title=cleaned_title,
            description=cleaned_description,
            priority=cleaned_priority,
            due_date=cleaned_due,
            status=cleaned_status,
        )
        save_all(self.storage, tasks=tasks)
        return task

    def _collect_contributors(self, user_ids: list[str]) -> list[str]:
        collected: list[str] = []
        for user_id in user_ids:
            user = require_user(self.storage, user_id)
            if user.id not in collected:
                collected.append(user.id)
        return collected


def _timestamp() -> str:
    return datetime.now().isoformat(timespec="seconds")
