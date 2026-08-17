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

    sqlite3.Row allows us to access columns using names:
    row["id"], row["title"], row["done"]
    """
    connection = sqlite3.connect(DATABASE_NAME)
    connection.row_factory = sqlite3.Row
    return connection


def row_to_task(row):
    """
    Convert a SQLite row into the dictionary format
    returned by the API.
    """
    return {
        "id": row["id"],
        "title": row["title"],
        "done": bool(row["done"]),
    }


def initialize_database():
    """
    Create the tasks table if it does not already exist.

    Insert the three example tasks only when
    the table is completely empty.
    """

    with sqlite3.connect(DATABASE_NAME) as connection:

        # Create the tasks table
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY,
                title TEXT NOT NULL,
                done INTEGER NOT NULL DEFAULT 0
            )
            """
        )

        # Count existing tasks
        row_count = connection.execute(
            "SELECT COUNT(*) FROM tasks"
        ).fetchone()[0]

        # Seed only when database is empty
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


# Initialize the database when application starts
initialize_database()


# --------------------------------------------------
# Temporary In-Memory Data
# --------------------------------------------------
#
# Stage 2 status:
#
# GET    -> SQLite
# POST   -> SQLite
# PUT    -> memory temporarily
# DELETE -> memory temporarily
#
# This list will be removed in Stage 3.
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
    return {
        "status": "ok"
    }


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

    return [
        row_to_task(row)
        for row in rows
    ]


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
            """
            SELECT *
            FROM tasks
            WHERE id = ?
            """,
            (task_id,),
        ).fetchone()

    # No matching task
    if row is None:
        return JSONResponse(
            status_code=404,
            content={
                "error": "Task not found"
            },
        )

    return row_to_task(row)


# --------------------------------------------------
# CREATE - Add New Task
# SQLite-backed
# --------------------------------------------------

@app.post(
    "/tasks",
    status_code=201,
    description="Create a new task in the SQLite database.",
)
def create_task(
    payload: dict | None = Body(default=None),
):

    # ----------------------------------------------
    # Validate request body
    # ----------------------------------------------

    if payload is None:
        return JSONResponse(
            status_code=400,
            content={
                "error": "Title is required"
            },
        )

    # Get title safely
    title = payload.get("title")

    # Title must be a non-empty string
    if not isinstance(title, str) or not title.strip():
        return JSONResponse(
            status_code=400,
            content={
                "error": "Title is required and cannot be empty"
            },
        )

    # Remove unnecessary spaces
    clean_title = title.strip()

    # ----------------------------------------------
    # Insert task into SQLite
    # ----------------------------------------------

    with get_connection() as connection:

        cursor = connection.execute(
            """
            INSERT INTO tasks (title, done)
            VALUES (?, ?)
            """,
            (
                clean_title,
                0,
            ),
        )

        # SQLite generated the ID for us
        new_task_id = cursor.lastrowid

    # ----------------------------------------------
    # Return the created task
    # ----------------------------------------------

    return {
        "id": new_task_id,
        "title": clean_title,
        "done": False,
    }


# --------------------------------------------------
# UPDATE - Update Existing Task
# TEMPORARILY still in memory
# Will move to SQLite in Stage 3
# --------------------------------------------------

@app.put(
    "/tasks/{task_id}",
    description="Update the title and/or completion status of a task.",
)
def update_task(
    task_id: int,
    payload: dict | None = Body(default=None),
):

    # Body must contain something
    if payload is None or not payload:
        return JSONResponse(
            status_code=400,
            content={
                "error": "At least one field is required"
            },
        )

    # Check which fields were provided
    has_title = "title" in payload
    has_done = "done" in payload

    # Must provide title and/or done
    if not has_title and not has_done:
        return JSONResponse(
            status_code=400,
            content={
                "error": "Provide title and/or done"
            },
        )

    # ----------------------------------------------
    # Validate title
    # ----------------------------------------------

    if has_title:

        title = payload["title"]

        if not isinstance(title, str) or not title.strip():
            return JSONResponse(
                status_code=400,
                content={
                    "error": "Title must be a non-empty string"
                },
            )

    # ----------------------------------------------
    # Validate done
    # ----------------------------------------------

    if has_done:

        done = payload["done"]

        if not isinstance(done, bool):
            return JSONResponse(
                status_code=400,
                content={
                    "error": "Done must be true or false"
                },
            )

    # ----------------------------------------------
    # Temporary in-memory update
    # ----------------------------------------------

    for task in tasks:

        if task["id"] == task_id:

            if has_title:
                task["title"] = payload["title"].strip()

            if has_done:
                task["done"] = payload["done"]

            return task

    # Task does not exist
    return JSONResponse(
        status_code=404,
        content={
            "error": f"Task {task_id} not found"
        },
    )


# --------------------------------------------------
# DELETE - Delete Existing Task
# TEMPORARILY still in memory
# Will move to SQLite in Stage 3
# --------------------------------------------------

@app.delete(
    "/tasks/{task_id}",
    description="Delete a task by its ID.",
)
def delete_task(task_id: int):

    # enumerate gives:
    # index -> position in the list
    # task  -> task dictionary

    for index, task in enumerate(tasks):

        if task["id"] == task_id:

            # Remove from temporary Python list
            tasks.pop(index)

            # HTTP 204 must have an empty body
            return Response(
                status_code=204
            )

    return JSONResponse(
        status_code=404,
        content={
            "error": f"Task {task_id} not found"
        },
    )