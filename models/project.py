"""A project owned by one user and shared with members."""


class Project:
    """Work tracked for a team.

    One user owns the project. Many users can be members. One project holds
    many tasks, stored here as task IDs.
    """

    VALID_STATUSES = ("Planning", "Active", "Completed", "Archived")

    def __init__(
        self,
        id: str,
        name: str,
        description: str,
        owner_id: str,
        member_ids: list[str] | None = None,
        task_ids: list[str] | None = None,
        status: str = "Planning",
        created_at: str = "",
    ) -> None:
        self.id = _required_text(id, "Project ID").upper()
        self.name = _required_text(name, "Project name")
        self.description = _required_text(description, "Description")
        self.owner_id = _required_text(owner_id, "Project owner").upper()
        self.member_ids = _unique_ids(member_ids)
        self.task_ids = _unique_ids(task_ids)
        self.status = _require_status(status)
        self.created_at = _required_text(created_at, "Created at")
        self.add_member(self.owner_id)

    def add_member(self, user_id: str) -> bool:
        """Add a user ID. Return False when that user is already a member."""
        cleaned = _required_text(user_id, "User ID").upper()
        if cleaned in self.member_ids:
            return False
        self.member_ids.append(cleaned)
        return True

    def remove_member(self, user_id: str) -> None:
        """Remove a member. The owner stays on the project."""
        cleaned = user_id.strip().upper()
        if cleaned == self.owner_id:
            return
        if cleaned in self.member_ids:
            self.member_ids.remove(cleaned)

    def add_task(self, task_id: str) -> None:
        """Attach a task ID if it is not already listed."""
        cleaned = _required_text(task_id, "Task ID").upper()
        if cleaned not in self.task_ids:
            self.task_ids.append(cleaned)

    def has_member(self, user_id: str) -> bool:
        """Return True when the user owns or belongs to the project."""
        return user_id == self.owner_id or user_id in self.member_ids

    def update(
        self,
        name: str | None = None,
        description: str | None = None,
        status: str | None = None,
    ) -> None:
        """Change the editable project fields."""
        if name is not None:
            self.name = _required_text(name, "Project name")
        if description is not None:
            self.description = _required_text(description, "Description")
        if status is not None:
            self.status = _require_status(status)

    def to_dict(self) -> dict:
        """Serialize the project for JSON storage."""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "owner_id": self.owner_id,
            "member_ids": list(self.member_ids),
            "task_ids": list(self.task_ids),
            "status": self.status,
            "created_at": self.created_at,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Project":
        """Rebuild a project from a JSON object."""
        return cls(
            id=data["id"],
            name=data["name"],
            description=data["description"],
            owner_id=data["owner_id"],
            member_ids=data.get("member_ids", []),
            task_ids=data.get("task_ids", []),
            status=data["status"],
            created_at=data["created_at"],
        )

    def __str__(self) -> str:
        return f"{self.id} - {self.name}"

    def __repr__(self) -> str:
        return (
            f"Project(id={self.id!r}, name={self.name!r}, "
            f"owner_id={self.owner_id!r}, status={self.status!r})"
        )


def _required_text(value: object, label: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{label} cannot be empty.")
    return value.strip()


def _require_status(status: object) -> str:
    if not isinstance(status, str):
        raise ValueError("Project status is invalid.")
    for choice in Project.VALID_STATUSES:
        if status.strip().casefold() == choice.casefold():
            return choice
    options = ", ".join(Project.VALID_STATUSES)
    raise ValueError(f"Invalid project status. Choose one of: {options}.")


def _unique_ids(values: list[str] | None) -> list[str]:
    if values is None:
        return []
    if not isinstance(values, list):
        raise ValueError("ID lists must be JSON arrays of strings.")
    unique: list[str] = []
    for value in values:
        if not isinstance(value, str) or not value.strip():
            raise ValueError("ID lists must contain non-empty strings.")
        cleaned = value.strip().upper()
        if cleaned not in unique:
            unique.append(cleaned)
    return unique
