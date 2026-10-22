"""A unit of work that belongs to one project."""


class Task:
    """Work inside a project.

    A task belongs to exactly one project. Many users can contribute to it,
    and one user can contribute to many tasks.
    """

    VALID_STATUSES = ("Pending", "In Progress", "Completed")
    VALID_PRIORITIES = ("Low", "Medium", "High", "Critical")

    def __init__(
        self,
        id: str,
        title: str,
        description: str,
        project_id: str,
        contributor_ids: list[str] | None = None,
        status: str = "Pending",
        priority: str = "Medium",
        due_date: str = "",
        created_at: str = "",
    ) -> None:
        self.id = _required_text(id, "Task ID").upper()
        self.title = _required_text(title, "Task title")
        self.description = _required_text(description, "Description")
        self.project_id = _required_text(project_id, "Project ID").upper()
        self.contributor_ids = _unique_ids(contributor_ids)
        self.status = _require_choice(status, self.VALID_STATUSES, "task status")
        self.priority = _require_choice(priority, self.VALID_PRIORITIES, "priority")
        self.due_date = _required_text(due_date, "Due date")
        self.created_at = _required_text(created_at, "Created at")

    def assign_contributor(self, user_id: str) -> bool:
        """Add a contributor. Return False when that user is already assigned."""
        cleaned = _required_text(user_id, "User ID").upper()
        if cleaned in self.contributor_ids:
            return False
        self.contributor_ids.append(cleaned)
        return True

    def remove_contributor(self, user_id: str) -> None:
        """Remove a contributor when they are currently assigned."""
        cleaned = user_id.strip().upper()
        if cleaned in self.contributor_ids:
            self.contributor_ids.remove(cleaned)

    def mark_complete(self) -> None:
        """Set the task status to Completed."""
        self.status = "Completed"

    def is_complete(self) -> bool:
        """Return True when the task status is Completed."""
        return self.status == "Completed"

    def update(
        self,
        title: str | None = None,
        description: str | None = None,
        priority: str | None = None,
        due_date: str | None = None,
        status: str | None = None,
    ) -> None:
        """Change the editable task fields."""
        if title is not None:
            self.title = _required_text(title, "Task title")
        if description is not None:
            self.description = _required_text(description, "Description")
        if priority is not None:
            self.priority = _require_choice(priority, self.VALID_PRIORITIES, "priority")
        if due_date is not None:
            self.due_date = _required_text(due_date, "Due date")
        if status is not None:
            self.status = _require_choice(status, self.VALID_STATUSES, "task status")

    def to_dict(self) -> dict:
        """Serialize the task for JSON storage."""
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "project_id": self.project_id,
            "contributor_ids": list(self.contributor_ids),
            "status": self.status,
            "priority": self.priority,
            "due_date": self.due_date,
            "created_at": self.created_at,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Task":
        """Rebuild a task from a JSON object."""
        return cls(
            id=data["id"],
            title=data["title"],
            description=data["description"],
            project_id=data["project_id"],
            contributor_ids=data.get("contributor_ids", []),
            status=data["status"],
            priority=data["priority"],
            due_date=data["due_date"],
            created_at=data["created_at"],
        )

    def __str__(self) -> str:
        return f"{self.id} - {self.title}"

    def __repr__(self) -> str:
        return (
            f"Task(id={self.id!r}, title={self.title!r}, "
            f"project_id={self.project_id!r}, status={self.status!r})"
        )


def _required_text(value: object, label: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{label} cannot be empty.")
    return value.strip()


def _require_choice(value: object, choices: tuple[str, ...], label: str) -> str:
    if not isinstance(value, str):
        raise ValueError(f"Invalid {label}.")
    for choice in choices:
        if value.strip().casefold() == choice.casefold():
            return choice
    options = ", ".join(choices)
    raise ValueError(f"Invalid {label}. Choose one of: {options}.")


def _unique_ids(values: list[str] | None) -> list[str]:
    if values is None:
        return []
    if not isinstance(values, list):
        raise ValueError("Contributor IDs must be a JSON array of strings.")
    unique: list[str] = []
    for value in values:
        if not isinstance(value, str) or not value.strip():
            raise ValueError("Contributor IDs must contain non-empty strings.")
        cleaned = value.strip().upper()
        if cleaned not in unique:
            unique.append(cleaned)
    return unique
