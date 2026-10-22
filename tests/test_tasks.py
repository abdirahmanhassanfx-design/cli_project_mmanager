"""Tests for tasks, contributors, and completion."""

import pytest

from storage.json_storage import JsonStorage
from services.task_service import TaskService
from utils.exceptions import NotFoundError, ValidationError


def _owner_and_project(db):
    owner = db["users"].create_user("John Doe", "john@example.com", "Developer")
    project = db["projects"].create_project(
        "E-Commerce Platform",
        "Online shopping platform",
        owner.id,
    )
    return owner, project


def test_create_task_links_it_to_the_project(db):
    _owner, project = _owner_and_project(db)

    task = db["tasks"].create_task(
        project.id,
        "Implement Authentication",
        "Build user login functionality",
        "high",
        "2026-11-01",
    )

    assert task.id == "T001"
    assert task.project_id == project.id
    assert task.priority == "High"
    assert task.status == "Pending"
    assert task.due_date == "2026-11-01"
    assert db["projects"].find_project(project.id).task_ids == ["T001"]


def test_task_requires_a_real_project_priority_and_date(db):
    _owner, project = _owner_and_project(db)

    with pytest.raises(NotFoundError):
        db["tasks"].create_task("P999", "Title", "Details", "Low", "2026-11-01")
    with pytest.raises(ValidationError):
        db["tasks"].create_task(project.id, "Title", "Details", "Urgent", "2026-11-01")
    with pytest.raises(ValidationError):
        db["tasks"].create_task(project.id, "Title", "Details", "Low", "11/01/2026")

    assert db["tasks"].list_tasks() == []
    assert db["projects"].find_project(project.id).task_ids == []


def test_contributors_are_many_to_many(db):
    john, project = _owner_and_project(db)
    jane = db["users"].create_user("Jane Smith", "jane@example.com", "Designer")
    david = db["users"].create_user("David Lee", "david@example.com", "Developer")
    login = db["tasks"].create_task(
        project.id,
        "Implement Authentication",
        "Build login",
        "High",
        "2026-11-01",
        [john.id, jane.id],
    )
    dashboard = db["tasks"].create_task(
        project.id,
        "Build Dashboard",
        "Show orders",
        "Medium",
        "2026-12-01",
        [jane.id],
    )

    db["tasks"].assign_contributor(dashboard.id, david.id)
    with pytest.raises(ValidationError):
        db["tasks"].assign_contributor(login.id, "u002")

    login = db["tasks"].find_task(login.id)
    dashboard = db["tasks"].find_task(dashboard.id)
    assert login.contributor_ids == [john.id, jane.id]
    assert dashboard.contributor_ids == [jane.id, david.id]
    jane_tasks = {task.id for task in db["tasks"].tasks_for_user(jane.id)}
    assert jane_tasks == {login.id, dashboard.id}
    assert [task.id for task in db["tasks"].tasks_for_project(project.id)] == [
        login.id,
        dashboard.id,
    ]


def test_unknown_contributor_does_not_save_the_task(db):
    _owner, project = _owner_and_project(db)

    with pytest.raises(NotFoundError):
        db["tasks"].create_task(
            project.id,
            "Title",
            "Details",
            "Low",
            "2026-11-01",
            ["U999"],
        )

    assert db["tasks"].list_tasks() == []


def test_mark_complete_is_saved(db):
    _owner, project = _owner_and_project(db)
    task = db["tasks"].create_task(
        project.id,
        "Implement Authentication",
        "Build login",
        "High",
        "2026-11-01",
    )

    completed = db["tasks"].mark_complete("t001")

    assert completed.is_complete()
    assert completed.status == "Completed"
    reloaded = TaskService(JsonStorage(db["path"]))
    assert reloaded.find_task(task.id).status == "Completed"


def test_edit_task_updates_the_saved_fields(db):
    _owner, project = _owner_and_project(db)
    task = db["tasks"].create_task(
        project.id,
        "Draft",
        "First pass",
        "Low",
        "2026-11-01",
    )

    updated = db["tasks"].update_task(
        task.id,
        title="Implement Authentication",
        description="Build login",
        priority="critical",
        due_date="2026-12-01",
        status="in progress",
    )

    assert updated.title == "Implement Authentication"
    assert updated.description == "Build login"
    assert updated.priority == "Critical"
    assert updated.due_date == "2026-12-01"
    assert updated.status == "In Progress"
