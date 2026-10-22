"""A person who can own projects and contribute to tasks."""


class User:
    """Someone tracked by the system.

    Projects point at a user through ``owner_id`` and ``member_ids``. Tasks
    point at users through ``contributor_ids``. The user record itself stores
    only this person's own details.
    """

    def __init__(self, id: str, name: str, email: str, role: str) -> None:
        self.id = _required_text(id, "User ID").upper()
        self.name = _required_text(name, "Name")
        self.email = _required_text(email, "Email")
        self.role = _required_text(role, "Role")

    def update(self, name: str | None = None, email: str | None = None, role: str | None = None) -> None:
        """Change the fields that were provided."""
        if name is not None:
            self.name = _required_text(name, "Name")
        if email is not None:
            self.email = _required_text(email, "Email")
        if role is not None:
            self.role = _required_text(role, "Role")

    def to_dict(self) -> dict:
        """Serialize the user for JSON storage."""
        return {
            "id": self.id,
            "name": self.name,
            "email": self.email,
            "role": self.role,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "User":
        """Rebuild a user from a JSON object."""
        return cls(
            id=data["id"],
            name=data["name"],
            email=data["email"],
            role=data["role"],
        )

    def __str__(self) -> str:
        return f"{self.id} - {self.name}"

    def __repr__(self) -> str:
        return (
            f"User(id={self.id!r}, name={self.name!r}, "
            f"email={self.email!r}, role={self.role!r})"
        )


def _required_text(value: object, label: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{label} cannot be empty.")
    return value.strip()
