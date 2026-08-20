from fastapi import Body, FastAPI, Response
from fastapi.responses import JSONResponse

import repository


app = FastAPI(
    title="Task API",
    description="A CRUD Task API backed by PostgreSQL.",
    version="1.0",
)


# Create table and seed data
repository.initialize_database()


# --------------------------------------------------
# Root
# --------------------------------------------------

@app.get("/")
def root():
    return {
        "name": "Task API",
        "version": "1.0",
    }


# --------------------------------------------------
# Health
# --------------------------------------------------

@app.get("/health")
def health():
    return {
        "status": "ok"
    }


# --------------------------------------------------
# READ ALL
# --------------------------------------------------

@app.get("/tasks")
def get_tasks():
    return repository.get_all_tasks()


# --------------------------------------------------
# READ ONE
# --------------------------------------------------

@app.get("/tasks/{task_id}")
def get_task(task_id: int):

    task = repository.get_task(task_id)

    if task is None:
        return JSONResponse(
            status_code=404,
            content={
                "error": "Task not found"
            },
        )

    return task


# --------------------------------------------------
# CREATE
# --------------------------------------------------

@app.post(
    "/tasks",
    status_code=201,
)
def create_task(
    payload: dict | None = Body(default=None),
):

    if payload is None:
        return JSONResponse(
            status_code=400,
            content={
                "error": "Title is required"
            },
        )

    title = payload.get("title")

    if not isinstance(title, str) or not title.strip():
        return JSONResponse(
            status_code=400,
            content={
                "error": "Title is required and cannot be empty"
            },
        )

    return repository.create_task(
        title.strip()
    )


# --------------------------------------------------
# UPDATE
# --------------------------------------------------

@app.put("/tasks/{task_id}")
def update_task(
    task_id: int,
    payload: dict | None = Body(default=None),
):

    if payload is None or not payload:
        return JSONResponse(
            status_code=400,
            content={
                "error": "At least one field is required"
            },
        )

    has_title = "title" in payload
    has_done = "done" in payload

    if not has_title and not has_done:
        return JSONResponse(
            status_code=400,
            content={
                "error": "Provide title and/or done"
            },
        )

    title = None
    done = None

    if has_title:
        title = payload["title"]

        if not isinstance(title, str) or not title.strip():
            return JSONResponse(
                status_code=400,
                content={
                    "error": "Title must be a non-empty string"
                },
            )

        title = title.strip()

    if has_done:
        done = payload["done"]

        if not isinstance(done, bool):
            return JSONResponse(
                status_code=400,
                content={
                    "error": "Done must be true or false"
                },
            )

    updated_task = repository.update_task(
        task_id,
        title=title,
        done=done,
    )

    if updated_task is None:
        return JSONResponse(
            status_code=404,
            content={
                "error": f"Task {task_id} not found"
            },
        )

    return updated_task


# --------------------------------------------------
# DELETE
# --------------------------------------------------

@app.delete("/tasks/{task_id}")
def delete_task(task_id: int):

    deleted = repository.delete_task(task_id)

    if not deleted:
        return JSONResponse(
            status_code=404,
            content={
                "error": f"Task {task_id} not found"
            },
        )

    return Response(status_code=204)