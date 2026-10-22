# Project Management System

A terminal application for tracking users, projects, and tasks. Administrators create people, group them into projects, assign task contributors, and update completion status. Everything is stored in a local JSON file, so the data is still there the next time the program starts.

## Features

- Create, list, search, view, and edit users
- Create, list, search, view, and edit projects
- Assign users to more than one project
- Create, list, view, and edit tasks that belong to a project
- Assign several contributors to a task, and let one person contribute to several tasks
- Mark a task complete
- Search projects by ID, name, owner, or status
- Show every project assigned to one user
- Report project totals, task totals, and each user's workload
- Save every change to `data/database.json`
- Load a small set of sample records the first time the database is created
- Reject empty names, bad email addresses, unknown IDs, invalid statuses, and invalid dates without crashing

## Technologies

- Python 3.10 or newer
- JSON, through the standard library
- [Rich](https://github.com/Textualize/rich) for tables, panels, and colored messages
- pytest
- pip

## Installation

Clone the repository and move into the project folder (the folder that contains `app.py`):

```bash
git clone <repository-url>
cd project_tracker
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

On Windows, activate the virtual environment with:

```bash
venv\Scripts\activate
```

If Python 3 is not available as `python`, use `python3` in the commands above.

## Running the Application

From the project folder, with the virtual environment activated:

```bash
python app.py
```

The main menu stays open until you choose Exit:

```text
1. User Management
2. Project Management
3. Task Management
4. Search
5. Reports
6. Exit
```

A normal first session looks like this:

```text
Name: John Doe
Email: john@example.com
Role: Developer

User created successfully.
User ID: U001
```

```text
Project name: E-Commerce Platform
Description: Online shopping platform
Project owner: U001

Project created successfully.
Project ID: P001
```

```text
Project: P001
Task title: Implement Authentication
Description: Build user login functionality
Priority: High
Due date: 2026-11-01

Task created successfully.
Task ID: T001
```

Choose **Mark Task Complete**, enter the task ID, and the new status is written to disk immediately.

## Running Tests

From the project folder, with the virtual environment activated:

```bash
pytest
```

The tests create temporary database files. They do not change `data/database.json`.

## Project Structure

```text
app.py                      Starts the program and opens the main menu
requirements.txt            Packages to install with pip
pytest.ini                  Tells pytest where the tests live
data/database.json          Saved users, projects, and tasks
models/                     User, Project, and Task classes
services/user_service.py   Create, find, update, search, and delete users
services/project_service.py
                            Create, find, update, search, and assign projects
services/task_service.py   Create, find, update, assign, and complete tasks
services/report_service.py Project, task, and workload counts
services/seed.py            Sample records used on a brand-new database
services/bootstrap.py       Connects storage to the services
services/records.py         Turns JSON objects into model objects and back
storage/json_storage.py     load_data() and save_data()
cli/                        Menus, prompts, and Rich tables
utils/                      Email, date, and ID checks, plus error types
tests/                      Automated tests
```

The menus only ask questions and print results. The service classes decide whether a change is allowed. The storage module is the only place that reads and writes the file.

## How Records Relate

IDs connect the records. A full user or project is not copied into every related record.

- One user can own many projects (`project.owner_id`).
- One project can contain many tasks (`task.project_id` and `project.task_ids`).
- Many users can belong to many projects (`project.member_ids`). The owner is included in that list.
- Many users can contribute to many tasks (`task.contributor_ids`).

User IDs look like `U001`, project IDs like `P001`, and task IDs like `T001`. The program generates them.

## Sample Data

When `data/database.json` does not exist yet, the program creates it and inserts sample users, projects, and tasks:

| Users | Projects | Tasks |
| --- | --- | --- |
| John Doe | E-Commerce Platform | Design Database |
| Jane Smith | School Management System | Implement Authentication |
| David Lee | Mobile Banking Application | Build Dashboard |
| | | Write Tests |

Starting the program again does not add those records a second time, and it does not replace anything you have edited.

To see the first-run sample data again, quit the program and delete `data/database.json`. That removes every saved user, project, and task.

## Data File

Records are stored as JSON:

```json
{
    "users": [],
    "projects": [],
    "tasks": []
}
```

The default file is `data/database.json`, next to `app.py`. You can point at a different file by setting `PROJECT_TRACKER_DB` before you start the program:

```bash
PROJECT_TRACKER_DB=/tmp/demo.json python app.py
```

If the file is missing, it is created. If the file is not valid JSON, the program stops, explains the problem, and leaves the file as it is so you can fix it. A change that passes validation is saved before the menu asks for the next action.

## Input Rules

- Names, titles, descriptions, and roles cannot be blank.
- Email addresses must look like `name@example.com`.
- Two users cannot share the same email address.
- A project owner, project member, and task contributor must already exist.
- Project status must be Planning, Active, Completed, or Archived.
- Task status must be Pending, In Progress, or Completed.
- Priority must be Low, Medium, High, or Critical.
- Due dates use `YYYY-MM-DD`, for example `2026-11-01`.
- Menu choices outside the listed numbers are rejected with a short message.
- IDs can be typed in any letter case. `u001` and `U001` are the same user.

On an edit screen, press Enter to keep the value that is already stored.

## Troubleshooting

`ModuleNotFoundError: No module named 'rich'`

Activate the virtual environment and run `pip install -r requirements.txt`.

`The database file is not valid JSON`

The program did not overwrite the file. Repair `data/database.json`, or move it aside if you are ready to start over. A new file is created only when the original path is absent.
