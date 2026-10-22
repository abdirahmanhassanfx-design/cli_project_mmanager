"""Create, find, update, and delete users."""

from models.user import User
from services.records import load_projects, load_tasks, load_users, save_all
from storage.json_storage import JsonStorage
from utils.exceptions import NotFoundError, ValidationError
from utils.ids import next_id
from utils.validation import normalize_id, require_non_empty, validate_email


class UserService:
    """Business rules for user records."""

    def __init__(self, storage: JsonStorage) -> None:
        self.storage = storage

    def create_user(self, name: str, email: str, role: str) -> User:
        """Validate input, assign the next user ID, and save."""
        cleaned_name = require_non_empty(name, "Name")
        cleaned_email = validate_email(email)
        cleaned_role = require_non_empty(role, "Role")
        users = load_users(self.storage)
        self._ensure_unique_email(users, cleaned_email)
        user = User(
            id=next_id([item.id for item in users], "U"),
            name=cleaned_name,
            email=cleaned_email,
            role=cleaned_role,
        )
        users.append(user)
        save_all(self.storage, users=users)
        return user

    def list_users(self) -> list[User]:
        """Return users ordered by ID."""
        return sorted(load_users(self.storage), key=lambda user: user.id)

    def find_user(self, user_id: str) -> User:
        """Return the user with this ID."""
        normalized = normalize_id(user_id, "User")
        for user in self.list_users():
            if user.id == normalized:
                return user
        raise NotFoundError(f"No user found with ID {normalized}.")

    def search_users(self, query: str) -> list[User]:
        """Find users whose ID, name, or email contains the query."""
        cleaned = require_non_empty(query, "Search").casefold()
        matches = []
        for user in self.list_users():
            haystack = f"{user.id} {user.name} {user.email}".casefold()
            if cleaned in haystack:
                matches.append(user)
        return matches

    def update_user(
        self,
        user_id: str,
        name: str | None = None,
        email: str | None = None,
        role: str | None = None,
    ) -> User:
        """Change name, email, or role and save immediately."""
        users = load_users(self.storage)
        user = self._find_in(users, user_id)
        cleaned_name = require_non_empty(name, "Name") if name is not None else None
        cleaned_email = validate_email(email) if email is not None else None
        cleaned_role = require_non_empty(role, "Role") if role is not None else None
        if cleaned_email is not None:
            self._ensure_unique_email(users, cleaned_email, ignore_id=user.id)
        user.update(name=cleaned_name, email=cleaned_email, role=cleaned_role)
        save_all(self.storage, users=users)
        return user

    def delete_user(self, user_id: str) -> User:
        """Delete a user who does not own a project.

        Membership and task contribution links are removed. Owners must be
        replaced first, because a project always needs an owner.
        """
        users = load_users(self.storage)
        projects = load_projects(self.storage)
        tasks = load_tasks(self.storage)
        user = self._find_in(users, user_id)
        owned = [project for project in projects if project.owner_id == user.id]
        if owned:
            names = ", ".join(project.id for project in owned)
            raise ValidationError(
                f"Cannot delete {user.name} because they own {names}."
            )
        for project in projects:
            project.remove_member(user.id)
        for task in tasks:
            task.remove_contributor(user.id)
        remaining = [item for item in users if item.id != user.id]
        save_all(self.storage, users=remaining, projects=projects, tasks=tasks)
        return user

    def _find_in(self, users: list[User], user_id: str) -> User:
        normalized = normalize_id(user_id, "User")
        for user in users:
            if user.id == normalized:
                return user
        raise NotFoundError(f"No user found with ID {normalized}.")

    def _ensure_unique_email(
        self,
        users: list[User],
        email: str,
        ignore_id: str | None = None,
    ) -> None:
        for user in users:
            if user.id == ignore_id:
                continue
            if user.email.casefold() == email.casefold():
                raise ValidationError(f"A user with email {email} already exists.")
