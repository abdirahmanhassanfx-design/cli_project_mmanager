"""Start the project management CLI."""

import os
from pathlib import Path

from rich.markup import escape
from rich.panel import Panel

from cli.display import make_console
from cli.menu import Application
from services.bootstrap import open_tracker
from utils.exceptions import StorageError


def database_path() -> Path:
    """Return the JSON database path.

    ``PROJECT_TRACKER_DB`` overrides the default ``data/database.json`` location.
    The default stays next to this file, so the app finds its data no matter
    which directory it was started from.
    """
    override = os.environ.get("PROJECT_TRACKER_DB")
    if override:
        return Path(override)
    return Path(__file__).resolve().parent / "data" / "database.json"


def main() -> int:
    """Load data, seed a brand-new database, and open the menu."""
    console = make_console()
    path = database_path()
    try:
        storage, users, projects, tasks, reports = open_tracker(path)
    except StorageError as exc:
        console.print(
            Panel(escape(str(exc)), title="Storage Error", border_style="red")
        )
        return 1

    Application(
        users=users,
        projects=projects,
        tasks=tasks,
        reports=reports,
        database_path=path,
        seeded=storage.created_new,
    ).run()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
