"""Shared fixtures."""

from pathlib import Path

import pytest

from services.bootstrap import open_tracker


@pytest.fixture
def db(tmp_path: Path) -> dict:
    """Return services backed by a new, empty database."""
    path = tmp_path / "database.json"
    storage, users, projects, tasks, reports = open_tracker(path, seed_if_new=False)
    return {
        "path": path,
        "storage": storage,
        "users": users,
        "projects": projects,
        "tasks": tasks,
        "reports": reports,
    }
