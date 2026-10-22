"""Tests for projects, membership, and project search."""

import pytest

from services.bootstrap import open_tracker
from utils.exceptions import NotFoundError, ValidationError


def test_create_project_makes_the_owner_a_member(db):
    owner = db["users"].create_user("John Doe", "john@example.com", "Developer")

    project = db["projects"].create_project(
        "E-Commerce Platform",
        "Online shopping platform",
        owner.id,
    )

    assert project.id == "P001"
    assert project.owner_id == owner.id
    assert project.member_ids == [owner.id]
    assert project.status == "Planning"
    assert project.task_ids == []
    assert "T" in project.created_at


def test_missing_owner_does_not_create_a_project(db):
    with pytest.raises(NotFoundError):
        db["projects"].create_project("Orphan", "Nobody owns this", "U999")

    assert db["projects"].list_projects() == []


def test_user_can_belong_to_multiple_projects(db):
    jane = db["users"].create_user("Jane Smith", "jane@example.com", "Designer")
    john = db["users"].create_user("John Doe", "john@example.com", "Developer")
    school = db["projects"].create_project("School Management System", "Classes", jane.id)
    banking = db["projects"].create_project("Mobile Banking Application", "Transfers", john.id)

    db["projects"].assign_user(banking.id, jane.id)

    assigned = [project.id for project in db["projects"].projects_for_user(jane.id)]
    assert assigned == [school.id, banking.id]
    assert jane.id in db["projects"].find_project(banking.id).member_ids


def test_assigning_the_same_user_twice_is_rejected(db):
    owner = db["users"].create_user("John Doe", "john@example.com", "Developer")
    member = db["users"].create_user("Jane Smith", "jane@example.com", "Designer")
    project = db["projects"].create_project("Shop", "Online shop", owner.id)
    db["projects"].assign_user(project.id, member.id)

    with pytest.raises(ValidationError):
        db["projects"].assign_user(project.id, "u002")

    assert db["projects"].find_project(project.id).member_ids == [owner.id, member.id]


def test_search_projects_by_name_owner_status_and_id(db):
    jane = db["users"].create_user("Jane Smith", "jane@example.com", "Designer")
    john = db["users"].create_user("John Doe", "john@example.com", "Developer")
    school = db["projects"].create_project("School Management System", "Classes", jane.id)
    db["projects"].update_project(school.id, status="active")
    db["projects"].create_project("E-Commerce Platform", "Shop", john.id)

    assert [item.id for item in db["projects"].search_projects("school")] == [school.id]
    assert [item.id for item in db["projects"].search_projects("Jane")] == [school.id]
    assert [item.id for item in db["projects"].search_projects(school.id)] == [school.id]
    assert [item.status for item in db["projects"].search_projects("active")] == ["Active"]
    assert [item.owner_id for item in db["projects"].search_projects("john")] == [john.id]
    assert db["projects"].search_projects("missing") == []


def test_invalid_project_status_is_not_saved(db):
    owner = db["users"].create_user("John Doe", "john@example.com", "Developer")
    project = db["projects"].create_project("Shop", "Online shop", owner.id)

    with pytest.raises(ValidationError):
        db["projects"].update_project(project.id, status="Paused")

    assert db["projects"].find_project(project.id).status == "Planning"


def test_sample_user_sees_only_assigned_projects(tmp_path):
    _, users, projects, _, _ = open_tracker(tmp_path / "database.json")

    names = [project.name for project in projects.projects_for_user("U001")]

    assert users.find_user("U001").name == "John Doe"
    assert names == ["E-Commerce Platform", "Mobile Banking Application"]
