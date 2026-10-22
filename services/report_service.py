"""Counts used by the reports menu."""

from models.project import Project
from models.task import Task
from services.project_service import ProjectService
from services.task_service import TaskService
from services.user_service import UserService
from storage.json_storage import JsonStorage


class ReportService:
    """Read-only summaries across users, projects, and tasks."""

    def __init__(self, storage: JsonStorage) -> None:
        self.users = UserService(storage)
        self.projects = ProjectService(storage)
        self.tasks = TaskService(storage)

    def project_summary(self) -> dict[str, int]:
        """Count projects by status, plus a total."""
        summary = {status: 0 for status in Project.VALID_STATUSES}
        projects = self.projects.list_projects()
        for project in projects:
            summary[project.status] = summary.get(project.status, 0) + 1
        summary["total"] = len(projects)
        return summary

    def task_summary(self) -> dict[str, int]:
        """Count tasks by status, plus a total."""
        summary = {status: 0 for status in Task.VALID_STATUSES}
        tasks = self.tasks.list_tasks()
        for task in tasks:
            summary[task.status] = summary.get(task.status, 0) + 1
        summary["total"] = len(tasks)
        return summary

    def user_workload(self) -> list[dict[str, str | int]]:
        """Count projects and tasks associated with each user.

        Project count includes ownership and membership. Task count includes
        every task that lists the user as a contributor.
        """
        rows = []
        for user in self.users.list_users():
            project_count = len(self.projects.projects_for_user(user.id))
            task_count = len(self.tasks.tasks_for_user(user.id))
            rows.append(
                {
                    "id": user.id,
                    "name": user.name,
                    "projects": project_count,
                    "tasks": task_count,
                }
            )
        return rows
