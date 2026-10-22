"""Create, find, update, and assign projects."""

from datetime import datetime

from models.project import Project
from services.records import (
    find_project,
    load_projects,
    load_users,
    require_user,
    save_all,
)
from storage.json_storage import JsonStorage
from utils.exceptions import ValidationError
from utils.ids import next_id
from utils.validation import require_non_empty, validate_choice


class ProjectService:
    """Business rules for projects and their members."""

    def __init__(self, storage: JsonStorage) -> None:
        self.storage = storage

    def create_project(self, name: str, description: str, owner_id: str) -> Project:
        """Create a project owned by an existing user.

        The owner is also stored as a member, so membership checks have one list
        to read. New projects start in Planning.
        """
        cleaned_name = require_non_empty(name, "Project name")
        cleaned_description = require_non_empty(description, "Description")
        owner = require_user(self.storage, owner_id)
        projects = load_projects(self.storage)
        project = Project(
            id=next_id([item.id for item in projects], "P"),
            name=cleaned_name,
            description=cleaned_description,
            owner_id=owner.id,
            status="Planning",
            created_at=_timestamp(),
        )
        projects.append(project)
        save_all(self.storage, projects=projects)
        return project

    def list_projects(self) -> list[Project]:
        """Return projects ordered by ID."""
        return sorted(load_projects(self.storage), key=lambda project: project.id)

    def find_project(self, project_id: str) -> Project:
        """Return the project with this ID."""
        return find_project(self.list_projects(), project_id)

    def search_projects(self, query: str) -> list[Project]:
        """Find projects by ID, name, owner name, owner ID, or status."""
        cleaned = require_non_empty(query, "Search").casefold()
        owner_names = {user.id: user.name for user in load_users(self.storage)}
        matches = []
        for project in self.list_projects():
            owner_name = owner_names.get(project.owner_id, "")
            haystack = " ".join(
                [project.id, project.name, project.status, project.owner_id, owner_name]
            ).casefold()
            if cleaned in haystack:
                matches.append(project)
        return matches

    def projects_for_user(self, user_id: str) -> list[Project]:
        """Return every project the user owns or belongs to."""
        user = require_user(self.storage, user_id)
        return [
            project for project in self.list_projects() if project.has_member(user.id)
        ]

    def assign_user(self, project_id: str, user_id: str) -> Project:
        """Add an existing user to a project's members."""
        projects = load_projects(self.storage)
        project = find_project(projects, project_id)
        user = require_user(self.storage, user_id)
        if not project.add_member(user.id):
            raise ValidationError(f"{user.name} is already assigned to {project.name}.")
        save_all(self.storage, projects=projects)
        return project

    def update_project(
        self,
        project_id: str,
        name: str | None = None,
        description: str | None = None,
        status: str | None = None,
    ) -> Project:
        """Change name, description, or status and save immediately."""
        projects = load_projects(self.storage)
        project = find_project(projects, project_id)
        cleaned_name = require_non_empty(name, "Project name") if name is not None else None
        cleaned_description = (
            require_non_empty(description, "Description") if description is not None else None
        )
        cleaned_status = (
            validate_choice(status, Project.VALID_STATUSES, "project status")
            if status is not None
            else None
        )
        project.update(
            name=cleaned_name,
            description=cleaned_description,
            status=cleaned_status,
        )
        save_all(self.storage, projects=projects)
        return project


def _timestamp() -> str:
    return datetime.now().isoformat(timespec="seconds")
