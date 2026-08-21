from fastapi import Body, Depends, FastAPI, Request, Response
from fastapi.responses import JSONResponse
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from auth_client import supabase
import repository


# --------------------------------------------------
# FastAPI Application
# --------------------------------------------------

app = FastAPI(
    title="Task API",
    description=(
        "A CRUD Task API backed by PostgreSQL "
        "with Supabase authentication."
    ),
    version="1.0",
)


# --------------------------------------------------
# Database Initialization
# --------------------------------------------------

repository.initialize_database()


# --------------------------------------------------
# Authentication Security
# --------------------------------------------------

security = HTTPBearer(
    auto_error=False,
    scheme_name="BearerAuth",
    description="Enter your Supabase access token.",
)


class AuthError(Exception):
    def __init__(self, message: str):
        super().__init__(message)
        self.message = message


@app.exception_handler(AuthError)
async def auth_error_handler(
    request: Request,
    exc: AuthError,
):
    return JSONResponse(
        status_code=401,
        content={"error": exc.message},
    )


def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(security),
):
    """
    Reusable authentication dependency.

    Protected routes use this function to:
    1. Require a Bearer token.
    2. Verify the token with Supabase.
    3. Return the authenticated user and token.
    """

    if credentials is None:
        raise AuthError("Access token required")

    if credentials.scheme.lower() != "bearer":
        raise AuthError("Access token required")

    token = credentials.credentials.strip()

    if not token:
        raise AuthError("Access token required")

    try:
        response = supabase.auth.get_user(token)
        user = response.user

        if user is None:
            raise AuthError("Invalid or expired token")

    except AuthError:
        raise

    except Exception:
        raise AuthError("Invalid or expired token")

    return {
        "user": user,
        "token": token,
    }


# ==================================================
# GENERAL ROUTES
# ==================================================


# --------------------------------------------------
# Root
# --------------------------------------------------

@app.get("/")
def root():
    return {
        "name": "Task API",
        "version": "1.0",
        "authentication": "Supabase Auth",
        "database": "PostgreSQL",
    }


# --------------------------------------------------
# Health Check
# --------------------------------------------------

@app.get("/health")
def health():
    return {
        "status": "ok"
    }


# ==================================================
# AUTH ROUTES
# ==================================================


# --------------------------------------------------
# Sign Up
# --------------------------------------------------

@app.post(
    "/auth/signup",
    status_code=201,
)
def signup(
    payload: dict | None = Body(default=None),
):
    if payload is None:
        return JSONResponse(
            status_code=400,
            content={
                "error": "Email and password are required"
            },
        )

    email = payload.get("email")
    password = payload.get("password")

    if not isinstance(email, str) or not email.strip():
        return JSONResponse(
            status_code=400,
            content={
                "error": "Email is required"
            },
        )

    if not isinstance(password, str) or not password.strip():
        return JSONResponse(
            status_code=400,
            content={
                "error": "Password is required"
            },
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
                content={
                    "error": "Unable to create user"
                },
            )

        return {
            "user": {
                "id": str(response.user.id),
                "email": response.user.email,
                "created_at": str(
                    response.user.created_at
                ),
            }
        }

    except Exception:
        return JSONResponse(
            status_code=400,
            content={
                "error": "Unable to create user"
            },
        )


# --------------------------------------------------
# Log In
# --------------------------------------------------

@app.post("/auth/login")
def login(
    payload: dict | None = Body(default=None),
):
    if payload is None:
        return JSONResponse(
            status_code=400,
            content={
                "error": "Email and password are required"
            },
        )

    email = payload.get("email")
    password = payload.get("password")

    if not isinstance(email, str) or not email.strip():
        return JSONResponse(
            status_code=400,
            content={
                "error": "Email is required"
            },
        )

    if not isinstance(password, str) or not password.strip():
        return JSONResponse(
            status_code=400,
            content={
                "error": "Password is required"
            },
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
                content={
                    "error": "Invalid login credentials"
                },
            )

        return {
            "access_token": response.session.access_token,
            "refresh_token": response.session.refresh_token,
        }

    except Exception:
        return JSONResponse(
            status_code=401,
            content={
                "error": "Invalid login credentials"
            },
        )


# --------------------------------------------------
# Log Out
# Protected route
# --------------------------------------------------

@app.post(
    "/auth/logout",
    status_code=204,
)
def logout(
    auth=Depends(get_current_user),
):
    try:
        supabase.auth.sign_out()

        return Response(
            status_code=204
        )

    except Exception:
        return JSONResponse(
            status_code=400,
            content={
                "error": "Unable to log out"
            },
        )


# ==================================================
# PUBLIC / PROTECTED ROUTES
# ==================================================


# --------------------------------------------------
# Public Information
# --------------------------------------------------

@app.get("/public/info")
def public_info():
    return {
        "message": "Welcome stranger! This info is public."
    }


# --------------------------------------------------
# Protected Profile
# --------------------------------------------------

@app.get("/protected/profile")
def protected_profile(
    auth=Depends(get_current_user),
):
    user = auth["user"]

    return {
        "id": str(user.id),
        "email": user.email,
        "created_at": str(user.created_at),
    }


# --------------------------------------------------
# Protected Dashboard
# --------------------------------------------------

@app.get("/protected/dashboard")
def protected_dashboard(
    auth=Depends(get_current_user),
):
    user = auth["user"]

    return {
        "message": "Welcome to your protected dashboard",
        "user_id": str(user.id),
        "email": user.email,
    }


# ==================================================
# TASK CRUD ROUTES
# ==================================================


# --------------------------------------------------
# READ - All Tasks
# --------------------------------------------------

@app.get("/tasks")
def get_tasks():
    return repository.get_all_tasks()


# --------------------------------------------------
# READ - One Task
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
# CREATE - Task
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
                "error": (
                    "Title is required "
                    "and cannot be empty"
                )
            },
        )

    return repository.create_task(
        title.strip()
    )


# --------------------------------------------------
# UPDATE - Task
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
                    "error": (
                        "Title must be a non-empty string"
                    )
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
# DELETE - Task
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

    return Response(
        status_code=204
    )