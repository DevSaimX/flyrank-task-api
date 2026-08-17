from fastapi import Body, FastAPI, Response
from fastapi.responses import JSONResponse


# --------------------------------------------------
# FastAPI Application
# --------------------------------------------------

app = FastAPI(
    title="Task API",
    description="A simple in-memory CRUD API for managing tasks.",
    version="1.0",
)


# --------------------------------------------------
# In-Memory Data
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
    description="Return basic information about the Task API.",
)
def root():
    return {
        "name": "Task API",
        "version": "1.0",
        "endpoints": ["/tasks"],
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
# --------------------------------------------------

@app.get(
    "/tasks",
    description="Return all tasks currently stored in memory.",
)
def get_tasks():
    return tasks


# --------------------------------------------------
# CREATE - Add New Task
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

    # Safely get the title from the request body
    title = payload.get("title")

    # Validate the title
    if not isinstance(title, str) or not title.strip():
        return JSONResponse(
            status_code=400,
            content={"error": "Title is required and cannot be empty"},
        )

    # Generate the next task ID
    next_id = max(
        (task["id"] for task in tasks),
        default=0,
    ) + 1

    # Create the new task
    new_task = {
        "id": next_id,
        "title": title.strip(),
        "done": False,
    }

    # Store it in memory
    tasks.append(new_task)

    return new_task


# --------------------------------------------------
# READ - Get One Task
# --------------------------------------------------

@app.get(
    "/tasks/{task_id}",
    description="Return a single task by its ID.",
)
def get_task(task_id: int):

    for task in tasks:
        if task["id"] == task_id:
            return task

    return JSONResponse(
        status_code=404,
        content={"error": f"Task {task_id} not found"},
    )


# --------------------------------------------------
# UPDATE - Update Existing Task
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
            content={"error": "At least one field is required"},
        )

    # Check which fields were provided
    has_title = "title" in payload
    has_done = "done" in payload

    # At least title or done must be present
    if not has_title and not has_done:
        return JSONResponse(
            status_code=400,
            content={"error": "Provide title and/or done"},
        )

    # Validate title if provided
    if has_title:
        title = payload["title"]

        if not isinstance(title, str) or not title.strip():
            return JSONResponse(
                status_code=400,
                content={"error": "Title must be a non-empty string"},
            )

    # Validate done if provided
    if has_done:
        done = payload["done"]

        if not isinstance(done, bool):
            return JSONResponse(
                status_code=400,
                content={"error": "Done must be true or false"},
            )

    # Find and update the task
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
        content={"error": f"Task {task_id} not found"},
    )


# --------------------------------------------------
# DELETE - Delete Existing Task
# --------------------------------------------------

@app.delete(
    "/tasks/{task_id}",
    description="Delete a task by its ID.",
)
def delete_task(task_id: int):

    # enumerate gives both:
    # index -> location in the list
    # task  -> actual task dictionary
    for index, task in enumerate(tasks):

        if task["id"] == task_id:

            # Remove task from the list
            tasks.pop(index)

            # 204 must have an empty response body
            return Response(status_code=204)

    return JSONResponse(
        status_code=404,
        content={"error": f"Task {task_id} not found"},
    )