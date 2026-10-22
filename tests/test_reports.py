"""Tests for the summary reports."""

from services.bootstrap import open_tracker


def test_empty_reports(db):
    projects = db["reports"].project_summary()
    tasks = db["reports"].task_summary()

    assert projects["total"] == 0
    assert projects["Active"] == 0
    assert tasks["total"] == 0
    assert db["reports"].user_workload() == []


def test_sample_report_counts(tmp_path):
    _, _, _, _, reports = open_tracker(tmp_path / "database.json")

    projects = reports.project_summary()
    tasks = reports.task_summary()
    workload = {row["name"]: row for row in reports.user_workload()}

    assert projects["total"] == 3
    assert projects["Active"] == 2
    assert projects["Planning"] == 1
    assert projects["Completed"] == 0
    assert projects["Archived"] == 0
    assert tasks == {
        "Pending": 3,
        "In Progress": 1,
        "Completed": 0,
        "total": 4,
    }
    assert workload["John Doe"]["projects"] == 2
    assert workload["John Doe"]["tasks"] == 2
    assert workload["Jane Smith"]["projects"] == 2
    assert workload["Jane Smith"]["tasks"] == 3
    assert workload["David Lee"]["projects"] == 2
    assert workload["David Lee"]["tasks"] == 2
