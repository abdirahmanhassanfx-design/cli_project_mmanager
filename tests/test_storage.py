"""Tests for JSON loading, saving, and first-run sample data."""

import pytest

from services.bootstrap import open_tracker
from services.project_service import ProjectService
from services.task_service import TaskService
from services.user_service import UserService
from storage.json_storage import JsonStorage, load_data, save_data
from utils.exceptions import StorageError


def test_load_data_creates_a_missing_file(tmp_path):
    path = tmp_path / "nested" / "database.json"

    assert load_data(path) == {"users": [], "projects": [], "tasks": []}
    assert path.exists()


def test_save_data_round_trip(tmp_path):
    path = tmp_path / "database.json"
    save_data(
        path,
        {"users": [{"id": "U001", "name": "Ada"}], "projects": [], "tasks": []},
    )

    assert load_data(path)["users"] == [{"id": "U001", "name": "Ada"}]


def test_save_then_load_preserves_relationships(tmp_path):
    path = tmp_path / "database.json"
    _, users, projects, tasks, _ = open_tracker(path, seed_if_new=False)
    user = users.create_user("Grace Hopper", "grace@example.com", "Engineer")
    project = projects.create_project("Compiler", "Language tools", user.id)
    task = tasks.create_task(
        project.id,
        "Parse input",
        "Read source text",
        "Critical",
        "2026-11-20",
        [user.id],
    )
    tasks.mark_complete(task.id)

    storage = JsonStorage(path)
    loaded_users = UserService(storage)
    loaded_projects = ProjectService(storage)
    loaded_tasks = TaskService(storage)
    loaded_project = loaded_projects.find_project(project.id)
    loaded_task = loaded_tasks.find_task(task.id)

    assert storage.created_new is False
    assert loaded_users.find_user(user.id).email == "grace@example.com"
    assert loaded_project.owner_id == user.id
    assert user.id in loaded_project.member_ids
    assert task.id in loaded_project.task_ids
    assert loaded_task.status == "Completed"
    assert loaded_task.priority == "Critical"
    assert loaded_task.contributor_ids == [user.id]


def test_corrupt_json_is_reported_and_left_unchanged(tmp_path):
    path = tmp_path / "database.json"
    path.write_text("{not json", encoding="utf-8")

    with pytest.raises(StorageError, match="not valid JSON"):
        JsonStorage(path)

    assert path.read_text(encoding="utf-8") == "{not json"


def test_wrong_json_shape_is_rejected(tmp_path):
    path = tmp_path / "database.json"
    path.write_text("[]", encoding="utf-8")

    with pytest.raises(StorageError):
        load_data(path)

    assert path.read_text(encoding="utf-8") == "[]"


def test_missing_collections_default_to_empty_lists(tmp_path):
    path = tmp_path / "database.json"
    path.write_text('{"users": []}', encoding="utf-8")

    storage = JsonStorage(path)

    assert storage.data["projects"] == []
    assert storage.data["tasks"] == []


def test_invalid_record_is_explained(tmp_path):
    path = tmp_path / "database.json"
    save_data(path, {"users": [{"id": "U001"}], "projects": [], "tasks": []})

    with pytest.raises(StorageError, match="missing required field"):
        UserService(JsonStorage(path)).list_users()


def test_sample_data_is_created_once(tmp_path):
    path = tmp_path / "database.json"
    _, users, projects, tasks, _ = open_tracker(path)
    users.create_user("Extra Person", "extra@example.com", "Tester")

    _, reloaded_users, reloaded_projects, reloaded_tasks, _ = open_tracker(path)

    assert [user.name for user in reloaded_users.list_users()] == [
        "John Doe",
        "Jane Smith",
        "David Lee",
        "Extra Person",
    ]
    assert len(projects.list_projects()) == 3
    assert len(reloaded_projects.list_projects()) == 3
    assert len(tasks.list_tasks()) == 4
    assert len(reloaded_tasks.list_tasks()) == 4
    assert reloaded_users.find_user("U004").email == "extra@example.com"
