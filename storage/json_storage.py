"""JSON file persistence for users, projects, and tasks."""

import json
from pathlib import Path

from utils.exceptions import StorageError

DATABASE_KEYS = ("users", "projects", "tasks")


def empty_database() -> dict:
    """Return a new database with the three required collections."""
    return {"users": [], "projects": [], "tasks": []}


def load_data(filepath: str | Path) -> dict:
    """Load the database from disk.

    When the file does not exist, an empty database is created and returned.
    Corrupt JSON and the wrong top-level shape raise ``StorageError`` without
    replacing the original file.
    """
    path = Path(filepath)
    if not path.exists():
        data = empty_database()
        save_data(path, data)
        return data
    return _read(path)


def save_data(filepath: str | Path, data: dict) -> None:
    """Write the database dictionary to disk.

    The write goes to a temporary file first and then replaces the real file,
    so a crash mid-write does not leave a half-written database.
    """
    path = Path(filepath)
    normalized = _validate_structure(data)
    _atomic_write(path, normalized)


class JsonStorage:
    """In-memory view of ``database.json`` that saves itself after changes."""

    def __init__(self, filepath: str | Path) -> None:
        self.filepath = Path(filepath)
        self.created_new = not self.filepath.exists()
        self.data = load_data(self.filepath)

    def save_data(self) -> None:
        """Persist the current data dictionary."""
        save_data(self.filepath, self.data)


def _read(path: Path) -> dict:
    try:
        with path.open(encoding="utf-8") as handle:
            raw = json.load(handle)
    except FileNotFoundError as exc:
        raise StorageError(f"Database file not found: {path}") from exc
    except json.JSONDecodeError as exc:
        raise StorageError(
            f"The database file is not valid JSON ({path}). "
            "Fix the file, or remove it so a new database can be created. "
            f"Details: line {exc.lineno}, column {exc.colno}."
        ) from exc
    except OSError as exc:
        raise StorageError(f"Could not read the database file: {exc}") from exc
    try:
        return _validate_structure(raw)
    except StorageError as exc:
        raise StorageError(f"{exc} File: {path}") from exc


def _validate_structure(data: object) -> dict:
    if not isinstance(data, dict):
        raise StorageError(
            "Database must be a JSON object with users, projects, and tasks."
        )
    normalized = {}
    for key in DATABASE_KEYS:
        value = data.get(key, [])
        if not isinstance(value, list):
            raise StorageError(f"Database field '{key}' must be a list.")
        normalized[key] = value
    return normalized


def _atomic_write(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    try:
        with temporary.open("w", encoding="utf-8") as handle:
            json.dump(data, handle, indent=4, ensure_ascii=False)
            handle.write("\n")
        temporary.replace(path)
    except OSError as exc:
        raise StorageError(f"Could not save the database file: {exc}") from exc
    finally:
        if temporary.exists():
            try:
                temporary.unlink()
            except OSError:
                pass
