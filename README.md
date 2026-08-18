# Task API

A simple in-memory CRUD API built with Python and FastAPI as part of the FlyRank Backend AI Engineering internship.

The API manages a to-do list and supports creating, reading, updating, and deleting tasks. It also includes validation, correct HTTP status codes, a health-check endpoint, and automatically generated Swagger UI documentation.

## Features

- Create tasks
- List all tasks
- Get a task by ID
- Update a task's title and/or completion status
- Delete tasks
- Request validation
- Custom `400` and `404` JSON error responses
- Health-check endpoint
- Interactive Swagger UI
- In-memory storage

## Tech Stack

- Python 3.10+
- FastAPI
- Uvicorn
- Swagger UI / OpenAPI

## Project Structure

```text
flyrank-task-api/
├── docs/
│   └── swagger-ui.png
├── .gitignore
├── main.py
├── requirements.txt
└── README.md
```

## Run Locally

### 1. Clone the repository

```bash
git clone < https://github.com/DevSaimX/flyrank-task-api.git>
cd flyrank-task-api
```

### 2. Create a virtual environment

```bash
python -m venv .venu
```

On Windows PowerShell, activate it with:

```powershell
.\.venu\Scripts\Activate.ps1
```

### 3. Install dependencies

```bash
python -m pip install -r requirements.txt
```

### 4. Start the API

```bash
python -m uvicorn main:app --reload
```

The API will be available at:

```text
http://localhost:8000
```

Interactive Swagger documentation:

```text
http://localhost:8000/docs
```

## API Endpoints

| Method | Endpoint | Description | Success Status |
|---|---|---|---|
| GET | `/` | Return basic API information | `200 OK` |
| GET | `/health` | Check whether the API is running | `200 OK` |
| GET | `/tasks` | Return all tasks | `200 OK` |
| GET | `/tasks/{task_id}` | Return one task by ID | `200 OK` |
| POST | `/tasks` | Create a new task | `201 Created` |
| PUT | `/tasks/{task_id}` | Update task title and/or completion status | `200 OK` |
| DELETE | `/tasks/{task_id}` | Delete a task | `204 No Content` |

## Example Task

```json
{
  "id": 1,
  "title": "Learn FastAPI basics",
  "done": false
}
```

## Example Request

```bash
curl -i http://localhost:8000/tasks
```

Example response:

```text
HTTP/1.1 200 OK
server: uvicorn
content-type: application/json

[{"id":1,"title":"Learn FastAPI basics","done":false},{"id":2,"title":"Build CRUD API","done":false},{"id":3,"title":"Test API endpoints","done":true}]
```

## Creating a Task

Request body:

```json
{
  "title": "Buy milk"
}
```

Successful response:

```json
{
  "id": 4,
  "title": "Buy milk",
  "done": false
}
```

Status:

```text
201 Created
```

## Validation

Creating a task without a valid title returns:

```json
{
  "error": "Title is required and cannot be empty"
}
```

with:

```text
400 Bad Request
```

Requesting an unknown task returns:

```json
{
  "error": "Task 99 not found"
}
```

with:

```text
404 Not Found
```

## Swagger UI

FastAPI automatically generates an OpenAPI specification and interactive Swagger documentation.

Open:

```text
http://localhost:8000/docs
```

The full CRUD API can be tested using Swagger's **Try it out** feature.

![Swagger UI](docs/swagger-ui.png)

## In-Memory Storage

This project intentionally uses in-memory storage rather than a database.

Tasks exist inside the running Python process, so newly created or modified tasks are lost when the server restarts. The original seed tasks are recreated when the application starts again.

This demonstrates why persistent backend applications use databases.

## CRUD Mapping

| CRUD | HTTP Method | Operation |
|---|---|---|
| Create | POST | Add a task |
| Read | GET | Retrieve tasks |
| Update | PUT | Modify a task |
| Delete | DELETE | Remove a task |

## Author

Built for the FlyRank Backend AI Engineering Internship — Week 2.