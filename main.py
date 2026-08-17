from fastapi import Body, FastAPI, Response
from fastapi.responses import JSONResponse

app = FastAPI()


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


@app.get("/")
def root():
    return {
        "name": "Task API",
        "version": "1.0",
        "endpoints": ["/tasks"],
    }


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/tasks")
def get_tasks():
    return tasks


@app.post("/tasks", status_code=201)
def create_task(payload: dict | None = Body(default=None)):
    if payload is None:
        return JSONResponse(
            status_code=400,
            content={"error": "Title is required"},
        )

    title = payload.get("title")

    if not isinstance(title, str) or not title.strip():
        return JSONResponse(
            status_code=400,
            content={"error": "Title is required and cannot be empty"},
        )

    next_id = max((task["id"] for task in tasks), default=0) + 1

    new_task = {
        "id": next_id,
        "title": title.strip(),
        "done": False,
    }

    tasks.append(new_task)

    return new_task

@app.put("/tasks/{task_id}")
def update_task(task_id: int, payload: dict | None = Body(default=None)):
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

@app.get("/tasks/{task_id}")
def get_task(task_id: int):
    for task in tasks:
        if task["id"] == task_id:
            return task

    return JSONResponse(
        status_code=404,
        content={"error": f"Task {task_id} not found"},
    )

@app.delete("/tasks/{task_id}")
def delete_task(task_id: int):
    for index, task in enumerate(tasks):
        if task["id"] == task_id:
            tasks.pop(index)
            return Response(status_code=204)

    return JSONResponse(
        status_code=404,
        content={"error": f"Task {task_id} not found"},
    )