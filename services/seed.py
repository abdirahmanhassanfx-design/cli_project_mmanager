"""Optional sample records for a first launch."""

from services.project_service import ProjectService
from services.task_service import TaskService
from services.user_service import UserService


def seed_sample_data(
    user_service: UserService,
    project_service: ProjectService,
    task_service: TaskService,
) -> None:
    """Insert a small set of users, projects, and tasks.

    Call this only when the database file was just created. Running it against
    an existing database would add another copy of the sample records.
    """
    john = user_service.create_user("John Doe", "john@example.com", "Developer")
    jane = user_service.create_user("Jane Smith", "jane@example.com", "Designer")
    david = user_service.create_user("David Lee", "david@example.com", "Developer")

    ecommerce = project_service.create_project(
        "E-Commerce Platform",
        "Online shopping platform for retail customers.",
        john.id,
    )
    project_service.update_project(ecommerce.id, status="Active")
    project_service.assign_user(ecommerce.id, jane.id)

    school = project_service.create_project(
        "School Management System",
        "Tools for classes, attendance, and grades.",
        jane.id,
    )
    project_service.assign_user(school.id, david.id)

    banking = project_service.create_project(
        "Mobile Banking Application",
        "Mobile app for balances, transfers, and alerts.",
        john.id,
    )
    project_service.update_project(banking.id, status="Active")
    project_service.assign_user(banking.id, david.id)

    design = task_service.create_task(
        ecommerce.id,
        "Design Database",
        "Model products, orders, and customers.",
        "Medium",
        "2026-11-15",
        [john.id, jane.id],
    )
    task_service.update_task(design.id, status="In Progress")

    task_service.create_task(
        ecommerce.id,
        "Implement Authentication",
        "Build user login and session handling.",
        "High",
        "2026-11-01",
        [john.id, david.id],
    )
    task_service.create_task(
        banking.id,
        "Build Dashboard",
        "Show balances and recent transactions.",
        "Medium",
        "2026-12-01",
        [david.id, jane.id],
    )
    task_service.create_task(
        school.id,
        "Write Tests",
        "Cover enrollment and grading workflows.",
        "Low",
        "2026-12-15",
        [jane.id],
    )
