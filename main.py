from fastapi import Body, FastAPI, Header, Response
from fastapi.responses import JSONResponse

from auth_client import supabase
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

# --------------------------------------------------
# AUTH - Sign Up
# --------------------------------------------------

@app.post("/auth/signup", status_code=201)
def signup(payload: dict | None = Body(default=None)):

    if payload is None:
        return JSONResponse(
            status_code=400,
            content={"error": "Email and password are required"},
        )

    email = payload.get("email")
    password = payload.get("password")

    if not isinstance(email, str) or not email.strip():
        return JSONResponse(
            status_code=400,
            content={"error": "Email is required"},
        )

    if not isinstance(password, str) or not password.strip():
        return JSONResponse(
            status_code=400,
            content={"error": "Password is required"},
        )

    try:
        response = supabase.auth.sign_up(
            {
                "email": email.strip(),
                "password": password,
            }
        )

        if response.user is None:
            return JSONResponse(
                status_code=400,
                content={"error": "Unable to create user"},
            )

        return {
            "user": {
                "id": str(response.user.id),
                "email": response.user.email,
                "created_at": str(response.user.created_at),
            }
        }

    except Exception as error:
        return JSONResponse(
            status_code=400,
            content={"error": str(error)},
        )


# --------------------------------------------------
# AUTH - Log In
# --------------------------------------------------

@app.post("/auth/login")
def login(payload: dict | None = Body(default=None)):

    if payload is None:
        return JSONResponse(
            status_code=400,
            content={"error": "Email and password are required"},
        )

    email = payload.get("email")
    password = payload.get("password")

    if not isinstance(email, str) or not email.strip():
        return JSONResponse(
            status_code=400,
            content={"error": "Email is required"},
        )

    if not isinstance(password, str) or not password:
        return JSONResponse(
            status_code=400,
            content={"error": "Password is required"},
        )

    try:
        response = supabase.auth.sign_in_with_password(
            {
                "email": email.strip(),
                "password": password,
            }
        )

        if response.session is None:
            return JSONResponse(
                status_code=401,
                content={"error": "Invalid login credentials"},
            )

        return {
            "access_token": response.session.access_token,
            "refresh_token": response.session.refresh_token,
        }

    except Exception:
        return JSONResponse(
            status_code=401,
            content={"error": "Invalid login credentials"},
        )


# --------------------------------------------------
# PUBLIC
# --------------------------------------------------

@app.get("/public/info")
def public_info():
    return {
        "message": "Welcome stranger! This info is public."
    }


# --------------------------------------------------
# PROTECTED - Stage 2
# Token presence only, not verification yet
# --------------------------------------------------

@app.get("/protected/profile")
def protected_profile(
    authorization: str | None = Header(default=None),
):

    if not authorization:
        return JSONResponse(
            status_code=401,
            content={"error": "Access token required"},
        )

    if not authorization.startswith("Bearer "):
        return JSONResponse(
            status_code=401,
            content={"error": "Access token required"},
        )

    token = authorization.removeprefix("Bearer ").strip()

    if not token:
        return JSONResponse(
            status_code=401,
            content={"error": "Access token required"},
        )

    return {
        "message": "Access token received"
    }

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


