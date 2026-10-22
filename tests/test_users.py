"""Tests for creating, finding, updating, and deleting users."""

import pytest

from storage.json_storage import JsonStorage
from services.user_service import UserService
from utils.exceptions import NotFoundError, ValidationError


def test_create_user_assigns_the_next_id(db):
    first = db["users"].create_user("John Doe", "john@example.com", "Developer")
    second = db["users"].create_user("Jane Smith", "jane@example.com", "Designer")

    assert first.id == "U001"
    assert first.name == "John Doe"
    assert first.email == "john@example.com"
    assert first.role == "Developer"
    assert second.id == "U002"
    assert [user.id for user in db["users"].list_users()] == ["U001", "U002"]


def test_find_user_accepts_lowercase_ids(db):
    db["users"].create_user("John Doe", "john@example.com", "Developer")

    found = db["users"].find_user("u001")

    assert found.name == "John Doe"


def test_missing_user_raises_not_found(db):
    with pytest.raises(NotFoundError):
        db["users"].find_user("U999")


def test_update_user_changes_name_email_and_role(db):
    user = db["users"].create_user("John Doe", "john@example.com", "Developer")

    updated = db["users"].update_user(
        user.id,
        name="John Smith",
        email="john.smith@example.com",
        role="Lead",
    )

    assert updated.name == "John Smith"
    assert updated.email == "john.smith@example.com"
    assert updated.role == "Lead"
    reloaded = UserService(JsonStorage(db["path"]))
    assert reloaded.find_user("U001").name == "John Smith"


def test_empty_name_and_invalid_email_are_rejected(db):
    with pytest.raises(ValidationError):
        db["users"].create_user("   ", "john@example.com", "Developer")
    with pytest.raises(ValidationError):
        db["users"].create_user("John Doe", "john.example.com", "Developer")

    assert db["users"].list_users() == []


def test_duplicate_email_is_rejected(db):
    db["users"].create_user("John Doe", "john@example.com", "Developer")

    with pytest.raises(ValidationError):
        db["users"].create_user("Johnny", "JOHN@example.com", "Designer")

    assert len(db["users"].list_users()) == 1


def test_search_users_matches_name_email_and_id(db):
    db["users"].create_user("John Doe", "john@example.com", "Developer")
    db["users"].create_user("Jane Smith", "jane@example.com", "Designer")

    assert [user.id for user in db["users"].search_users("jane")] == ["U002"]
    assert [user.id for user in db["users"].search_users("JOHN@example.com")] == ["U001"]
    assert [user.id for user in db["users"].search_users("u002")] == ["U002"]
    assert db["users"].search_users("nobody") == []


def test_delete_removes_memberships_but_protects_owners(db):
    owner = db["users"].create_user("John Doe", "john@example.com", "Developer")
    member = db["users"].create_user("Jane Smith", "jane@example.com", "Designer")
    project = db["projects"].create_project("Shop", "Online shop", owner.id)
    db["projects"].assign_user(project.id, member.id)
    task = db["tasks"].create_task(
        project.id,
        "Login",
        "Build login",
        "High",
        "2026-11-01",
        [member.id],
    )

    with pytest.raises(ValidationError):
        db["users"].delete_user(owner.id)
    db["users"].delete_user(member.id)

    assert db["users"].find_user(owner.id).name == "John Doe"
    with pytest.raises(NotFoundError):
        db["users"].find_user(member.id)
    assert member.id not in db["projects"].find_project(project.id).member_ids
    assert member.id not in db["tasks"].find_task(task.id).contributor_ids
