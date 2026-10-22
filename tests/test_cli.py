"""Tests that the terminal application starts and saves menu actions."""

import json
import os
import subprocess
import sys
from pathlib import Path

import app
from cli.menu import Application
from services.bootstrap import open_tracker

ROOT = Path(__file__).resolve().parents[1]


def test_modules_import_without_a_cycle():
    assert callable(app.main)
    assert Application is not None
    assert open_tracker is not None


def test_cli_exits_cleanly(tmp_path):
    result = _run(tmp_path / "database.json", "6\n")

    assert result.returncode == 0
    assert "PROJECT MANAGEMENT SYSTEM" in result.stdout
    assert "Sample data loaded" in result.stdout
    assert "Goodbye." in result.stdout


def test_invalid_menu_choice_is_explained(tmp_path):
    result = _run(tmp_path / "database.json", "9\n6\n")

    assert result.returncode == 0
    assert "Invalid choice. Please select an option from 1 to 6." in result.stdout


def test_cli_creates_a_user(tmp_path):
    database = tmp_path / "database.json"

    result = _run(
        database,
        "\n".join(
            [
                "1",
                "1",
                "Ada Lovelace",
                "ada@example.com",
                "Engineer",
                "",
                "6",
                "6",
            ]
        )
        + "\n",
    )

    assert result.returncode == 0, result.stdout + result.stderr
    assert "User created successfully." in result.stdout
    assert "U004" in result.stdout
    saved = json.loads(database.read_text(encoding="utf-8"))
    names = [user["name"] for user in saved["users"]]
    assert names == ["John Doe", "Jane Smith", "David Lee", "Ada Lovelace"]

    restarted = _run(database, "6\n")
    assert restarted.returncode == 0
    assert "Sample data loaded" not in restarted.stdout
    assert json.loads(database.read_text(encoding="utf-8"))["users"][-1]["name"] == (
        "Ada Lovelace"
    )


def test_cli_marks_a_task_complete(tmp_path):
    database = tmp_path / "database.json"

    result = _run(
        database,
        "\n".join(["3", "5", "T002", "", "7", "6"]) + "\n",
    )

    assert result.returncode == 0, result.stdout + result.stderr
    assert 'Task T002 "Implement Authentication" marked as Completed.' in result.stdout
    saved = json.loads(database.read_text(encoding="utf-8"))
    auth = next(task for task in saved["tasks"] if task["id"] == "T002")
    assert auth["status"] == "Completed"


def test_corrupt_database_stops_the_cli_without_replacing_the_file(tmp_path):
    database = tmp_path / "database.json"
    database.write_text("{bad", encoding="utf-8")

    result = _run(database, "")

    assert result.returncode == 1
    assert "not valid JSON" in result.stdout
    assert database.read_text(encoding="utf-8") == "{bad"


def _run(database: Path, commands: str) -> subprocess.CompletedProcess[str]:
    environment = os.environ.copy()
    environment["PROJECT_TRACKER_DB"] = str(database)
    environment["PYTHONUNBUFFERED"] = "1"
    return subprocess.run(
        [sys.executable, str(ROOT / "app.py")],
        input=commands,
        text=True,
        capture_output=True,
        env=environment,
        cwd=ROOT,
        timeout=20,
        check=False,
    )
