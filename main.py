from fastapi import Body, FastAPI, Response
from fastapi.responses import JSONResponse
import sqlite3


# --------------------------------------------------
# FastAPI Application
# --------------------------------------------------

app = FastAPI(
    title="Task API",
    description="A simple CRUD API for managing tasks.",
    version="1.0",
)


# --------------------------------------------------
# Database Configuration
# --------------------------------------------------

DATABASE_NAME = "tasks.db"


def get_connection():
    """
    Open a connection to the SQLite database.

    sqlite3.Row allows us to access columns by name:
    row["id"], row["title"], row["done"]
    instead of row[0], row[1], row[2].
    """
    connection = sqlite3.connect(DATABASE_NAME)
    connection.row_factory = sqlite3.Row
    return connection


def row_to_task(row):
    """
    Convert a SQLite row into the same dictionary
    structure used by our API.
    """
    return {
        "id": row["id"],
        "title": row["title"],
        "done": bool(row["done"]),
    }


def initialize_database():
    """
    Create the database table if it does not exist
    and seed three tasks only when the table is empty.
    """
    with sqlite3.connect(DATABASE_NAME) as connection:

        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY,
                title TEXT NOT NULL,
                done INTEGER NOT NULL DEFAULT 0
            )
            """
        )

        row_count = connection.execute(
            "SELECT COUNT(*) FROM tasks"
        ).fetchone()[0]

        if row_count == 0:
            connection.executemany(
                """
                INSERT INTO tasks (title, done)
                VALUES (?, ?)
                """,
                [
                    ("Learn FastAPI basics", 0),
                    ("Build CRUD API", 0),
                    ("Test API endpoints", 1),
                ],
            )


# Initialize database when application loads
initialize_database()


# --------------------------------------------------
# Temporary In-Memory Data
# --------------------------------------------------
#
# Stage 1:
# GET endpoints now use SQLite.
#
# POST, PUT and DELETE still use this list temporarily.
# We will migrate them to SQLite in Stages 2 and 3.
# --------------------------------------------------

tasks = [
    {
        "id": 1,
        "title": "Learn FastAPI basics",
        "done": False,
    },
    {
        "id": 2,
        "title": "Build CRUD API",
        "done": False,
    },
    {
        "id": 3,
        "title": "Test API endpoints",
        "done": True,
    },
]


# --------------------------------------------------
# Root Endpoint
# --------------------------------------------------

@app.get(
    "/",
    description="Return basic information about the API.",
)
def root():
    return {
        "name": "Task API",
        "version": "1.0",
    }


# --------------------------------------------------
# Health Check
# --------------------------------------------------

@app.get(
    "/health",
    description="Check whether the API server is running.",
)
def health():
    return {"status": "ok"}


# --------------------------------------------------
# READ - Get All Tasks
# SQLite-backed
# --------------------------------------------------

@app.get(
    "/tasks",
    description="Return all tasks stored in the SQLite database.",
)
def get_tasks():

    with get_connection() as connection:
        rows = connection.execute(
            "SELECT * FROM tasks"
        ).fetchall()

    return [row_to_task(row) for row in rows]


# --------------------------------------------------
# READ - Get One Task
# SQLite-backed
# --------------------------------------------------

@app.get(
    "/tasks/{task_id}",
    description="Return a single task by its ID.",
)
def get_task(task_id: int):

    with get_connection() as connection:
        row = connection.execute(
            "SELECT * FROM tasks WHERE id = ?",
            (task_id,),
        ).fetchone()

    if row is None:
        return JSONResponse(
            status_code=404,
            content={"error": "Task not found"},
        )

    return row_to_task(row)


# --------------------------------------------------
# CREATE - Add New Task
# Still in memory until Stage 2
# --------------------------------------------------

@app.post(
    "/tasks",
    status_code=201,
    description="Create a new task with a non-empty title.",
)
def create_task(payload: dict | None = Body(default=None)):

    # Check whether a request body was provided
    if payload is None:
        return JSONResponse(
            status_code=400,
            content={"error": "Title is required"},
        )

    # Safely get the title
    title = payload.get("title")

    # Validate title
    if not isinstance(title, str) or not title.strip():
        return JSONResponse(
            status_code=400,
            content={"error": "Title is required and cannot be empty"},
        )

    # Generate next ID
    next_id = max(
        (task["id"] for task in tasks),
        default=0,
    ) + 1

    new_task = {
        "id": next_id,
        "title": title.strip(),
        "done": False,
    }

    # Temporary in-memory storage
    tasks.append(new_task)

    return new_task


# --------------------------------------------------
# UPDATE - Update Existing Task
# Still in memory until Stage 3
# --------------------------------------------------

@app.put(
    "/tasks/{task_id}",
    description="Update the title and/or completion status of a task.",
)
def update_task(
    task_id: int,
    payload: dict | None = Body(default=None),
):

    if payload is None or not payload:
        return JSONResponse(
            status_code=400,
            content={"error": "At least one field is required"},
        )

    has_title = "title" in payload
    has_done = "done" in payload

    if not has_title and not has_done:
        return JSONResponse(
            status_code=400,
            content={"error": "Provide title and/or done"},
        )

    if has_title:
        title = payload["title"]

        if not isinstance(title, str) or not title.strip():
            return JSONResponse(
                status_code=400,
                content={"error": "Title must be a non-empty string"},
            )

    if has_done:
        done = payload["done"]

        if not isinstance(done, bool):
            return JSONResponse(
                status_code=400,
                content={"error": "Done must be true or false"},
            )

    for task in tasks:
        if task["id"] == task_id:

            if has_title:
                task["title"] = payload["title"].strip()

            if has_done:
                task["done"] = payload["done"]

            return task

    return JSONResponse(
        status_code=404,
        content={"error": f"Task {task_id} not found"},
    )


# --------------------------------------------------
# DELETE - Delete Existing Task
# Still in memory until Stage 3
# --------------------------------------------------

@app.delete(
    "/tasks/{task_id}",
    description="Delete a task by its ID.",
)
def delete_task(task_id: int):

    for index, task in enumerate(tasks):

        if task["id"] == task_id:

            tasks.pop(index)

            # HTTP 204 must have no response body
            return Response(status_code=204)

    return JSONResponse(
        status_code=404,
        content={"error": f"Task {task_id} not found"},
    )