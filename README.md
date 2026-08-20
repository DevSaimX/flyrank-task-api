Yes — replace your current SQLite-focused README with this **final BE-04 version**. It keeps the history of A1/A2 but makes PostgreSQL + Docker the current implementation, which matches the assignment requirements.  Your previous README was still documenting SQLite as the active storage layer, so this update corrects that. 

````md
# Task API

A CRUD API built with Python, FastAPI, PostgreSQL, and Docker as part of the FlyRank Backend AI Engineering Internship.

This project evolved through three storage layers while keeping the same API contract:

```text
A1: FastAPI -> Python memory
A2: FastAPI -> SQLite
A3 / BE-04: FastAPI -> PostgreSQL -> Docker volume
````

The API endpoints, request shapes, validation rules, response formats, and HTTP status codes stayed the same while the storage implementation changed.

---

## Features

* Create tasks
* List all tasks
* Get a task by ID
* Update task title and/or completion status
* Delete tasks
* PostgreSQL database
* PostgreSQL running in Docker
* Persistent Docker volume
* Automatic `tasks` table creation
* Three example tasks seeded only when the table is empty
* Parameterized SQL queries
* Database logic isolated in `repository.py`
* `.env` based configuration
* Committed `.env.example`
* Custom `400` and `404` JSON errors
* Correct HTTP status codes
* Health-check endpoint
* Swagger UI / OpenAPI
* Full stack starts with Docker Compose
* Data survives container restarts

---

## Tech Stack

* Python 3.10+
* FastAPI
* Uvicorn
* PostgreSQL 17
* Psycopg 3
* python-dotenv
* Docker
* Docker Compose
* Swagger UI / OpenAPI

---

## Architecture

The project started with in-memory storage:

```text
Client
   |
   v
FastAPI
   |
   v
Python List
```

It was then migrated to SQLite:

```text
Client
   |
   v
FastAPI
   |
   v
SQLite
   |
   v
tasks.db
```

The current version uses PostgreSQL:

```text
Client
   |
   v
FastAPI Routes
   |
   v
repository.py
   |
   v
Psycopg
   |
   v
PostgreSQL Container
   |
   v
Docker Volume
```

The routes do not contain PostgreSQL-specific SQL.

All database operations are kept inside:

```text
repository.py
```

This demonstrates that the storage layer can change without changing how clients use the API.

---

## Why PostgreSQL?

PostgreSQL is a real database server rather than a local database file.

Compared with SQLite, PostgreSQL is better suited for larger backend systems because it supports:

* multiple concurrent clients
* server-based database access
* strong relational database features
* production-scale applications
* transactions and advanced queries
* network-based connections

For this project PostgreSQL runs inside Docker, so PostgreSQL does not need to be installed directly on the host machine.

---

## Why Docker?

Docker provides a consistent environment for running the application and database.

Instead of installing PostgreSQL manually, the project uses the official PostgreSQL image.

Important Docker concepts used:

```text
Image
-> recipe for a container

Container
-> running instance of an image

Volume
-> persistent storage outside the container

Docker Compose
-> starts multiple services together
```

The stack contains two services:

```text
api
-> FastAPI application

db
-> PostgreSQL database
```

---

## Project Structure

```text
flyrank-task-api/
|
├── docs/
│   ├── swagger-ui.png
│   ├── sqlite-database.png
│   ├── postgres-docker.png
│   ├── BE-01_FastAPI_CRUD_Revision_Notes.md
│   └── BE-02_SQLite_CRUD_Revision_Notes.md
|
├── .dockerignore
├── .env.example
├── .gitignore
├── compose.yaml
├── Dockerfile
├── main.py
├── repository.py
├── requirements.txt
└── README.md
```

The real `.env` file is intentionally excluded from Git.

---

## Environment Variables

Create your local `.env` file using `.env.example`.

Example:

```env
POSTGRES_USER=postgres
POSTGRES_PASSWORD=YOUR_PASSWORD
POSTGRES_DB=tasks
DATABASE_URL=postgresql://postgres:YOUR_PASSWORD@db:5432/tasks
```

The real `.env` file is gitignored.

`.env.example` is committed so another developer knows which variables are required.

No real database credentials are hardcoded in the application source code.

---

## Run with Docker

### 1. Clone the repository

```bash
git clone https://github.com/DevSaimX/flyrank-task-api.git
cd flyrank-task-api
```

### 2. Create `.env`

On Linux/macOS:

```bash
cp .env.example .env
```

On Windows PowerShell:

```powershell
Copy-Item .env.example .env
```

Update the password values inside `.env`.

### 3. Start the entire stack

```bash
docker compose up --build
```

Docker Compose starts:

```text
FastAPI application
+
PostgreSQL database
+
persistent Docker volume
```

After the image has already been built, the stack can also be started with:

```bash
docker compose up
```

API:

```text
http://localhost:8000
```

Swagger UI:

```text
http://localhost:8000/docs
```

---

## Docker Compose Services

The project has two services.

### API

Runs the FastAPI application.

```text
api
```

It connects to PostgreSQL using:

```text
db:5432
```

Inside Docker Compose, `db` is the service name of the PostgreSQL container.

### Database

Runs:

```text
postgres:17
```

PostgreSQL data is stored in the named Docker volume:

```text
taskdata
```

---

## Database Schema

The application automatically creates the `tasks` table if it does not already exist.

```sql
CREATE TABLE IF NOT EXISTS tasks (
    id SERIAL PRIMARY KEY,
    title TEXT NOT NULL,
    done BOOLEAN NOT NULL DEFAULT FALSE
);
```

The table contains:

| Column  | Type    | Description                         |
| ------- | ------- | ----------------------------------- |
| `id`    | SERIAL  | Automatically generated primary key |
| `title` | TEXT    | Task title                          |
| `done`  | BOOLEAN | Completion status                   |

Three example tasks are inserted only when the table is empty.

---

## Repository Layer

All PostgreSQL-specific database code is located in:

```text
repository.py
```

The repository handles:

```text
SELECT
INSERT
UPDATE
DELETE
database connection
database initialization
seed data
```

The FastAPI routes call repository functions rather than containing SQL directly.

For example:

```text
FastAPI Route
      |
      v
repository.get_task()
      |
      v
PostgreSQL
```

This keeps database implementation separate from API behavior.

---

## API Endpoints

| Method | Endpoint           | Description                  | Success Status   |
| ------ | ------------------ | ---------------------------- | ---------------- |
| GET    | `/`                | Return API information       | `200 OK`         |
| GET    | `/health`          | Check whether API is running | `200 OK`         |
| GET    | `/tasks`           | Return all tasks             | `200 OK`         |
| GET    | `/tasks/{task_id}` | Return one task              | `200 OK`         |
| POST   | `/tasks`           | Create a task                | `201 Created`    |
| PUT    | `/tasks/{task_id}` | Update a task                | `200 OK`         |
| DELETE | `/tasks/{task_id}` | Delete a task                | `204 No Content` |

The endpoint behavior remained the same across the memory, SQLite, and PostgreSQL versions.

---

## CRUD and SQL Mapping

| CRUD   | HTTP   | PostgreSQL |
| ------ | ------ | ---------- |
| Create | POST   | `INSERT`   |
| Read   | GET    | `SELECT`   |
| Update | PUT    | `UPDATE`   |
| Delete | DELETE | `DELETE`   |

---

## Parameterized Queries

Dynamic values are passed separately from SQL.

Example:

```python
cursor.execute(
    """
    SELECT id, title, done
    FROM tasks
    WHERE id = %s
    """,
    (task_id,),
)
```

Psycopg uses:

```text
%s
```

as the query placeholder.

Parameterized queries avoid directly joining user-controlled values into SQL strings.

---

## Creating a Task

Example request:

```bash
curl -i -X POST http://localhost:8000/tasks \
  -H "Content-Type: application/json" \
  -d '{"title":"Postgres task"}'
```

Example response:

```text
HTTP/1.1 201 Created
content-type: application/json
```

```json
{
  "id": 4,
  "title": "Postgres task",
  "done": false
}
```

PostgreSQL creates the ID automatically.

The repository uses:

```sql
INSERT INTO tasks (title, done)
VALUES (%s, %s)
RETURNING id, title, done;
```

---

## Reading Tasks

Request:

```bash
curl -i http://localhost:8000/tasks
```

Example:

```text
HTTP/1.1 200 OK
```

The repository executes:

```sql
SELECT id, title, done
FROM tasks
ORDER BY id;
```

---

## Updating a Task

Example request:

```json
{
  "done": true
}
```

The API preserves the partial-update behavior from previous assignments.

The repository uses PostgreSQL `UPDATE`.

```sql
UPDATE tasks
SET title = %s, done = %s
WHERE id = %s
RETURNING id, title, done;
```

---

## Deleting a Task

The repository uses:

```sql
DELETE FROM tasks
WHERE id = %s
RETURNING id;
```

Successful deletion returns:

```text
204 No Content
```

with an empty response body.

---

## Validation

Missing or empty title:

```text
400 Bad Request
```

Example:

```json
{
  "error": "Title is required and cannot be empty"
}
```

Unknown task:

```text
404 Not Found
```

Example:

```json
{
  "error": "Task not found"
}
```

Successful operations use:

```text
200 OK
201 Created
204 No Content
```

The validation behavior remained consistent with the previous versions of the API.

---

## Persistence

PostgreSQL data is stored in the Docker volume:

```text
taskdata
```

Persistence was tested by:

1. Starting the stack with Docker Compose.
2. Creating a new task through `POST /tasks`.
3. Confirming the task with `GET /tasks`.
4. Stopping the complete stack:

```bash
docker compose down
```

5. Starting the stack again:

```bash
docker compose up
```

6. Calling:

```bash
curl http://localhost:8000/tasks
```

The previously created task was still present.

This proves that the database rows survive container restarts because they are stored in the persistent Docker volume rather than inside the disposable container filesystem.

---

## PostgreSQL Verification

The PostgreSQL database can be opened directly with:

```bash
docker compose exec db psql -U postgres -d tasks
```

List tables:

```sql
\dt
```

Example:

```text
Schema | Name  | Type  | Owner
-------+-------+-------+---------
public | tasks | table | postgres
```

Read the task rows:

```sql
SELECT * FROM tasks;
```

---

## PostgreSQL Database Screenshot

The following screenshot shows the `tasks` table running inside the Dockerized PostgreSQL database.

![PostgreSQL Docker Database](docs/postgres-docker.png)

---

## Storage Evolution

### Assignment 1

```text
FastAPI
   |
   v
Python List
```

Data disappeared when the application stopped.

### Assignment 2

```text
FastAPI
   |
   v
SQLite
   |
   v
tasks.db
```

Data survived application restarts.

### Assignment 3 / BE-04

```text
FastAPI
   |
   v
Repository
   |
   v
PostgreSQL
   |
   v
Docker Volume
```

Now both the application and database can run as a portable local stack.

---

## What Stayed the Same?

These endpoints remained unchanged:

```text
GET    /tasks
GET    /tasks/{task_id}
POST   /tasks
PUT    /tasks/{task_id}
DELETE /tasks/{task_id}
```

The API client does not need to know whether the storage engine is:

```text
memory
SQLite
PostgreSQL
```

This demonstrates that storage is an implementation detail behind the API contract.

---

## Swagger UI

FastAPI automatically generates interactive OpenAPI documentation.

Open:

```text
http://localhost:8000/docs
```

![Swagger UI](docs/swagger-ui.png)

---

## Useful Docker Commands

Start the stack:

```bash
docker compose up
```

Start and rebuild:

```bash
docker compose up --build
```

Stop the stack:

```bash
docker compose down
```

View running containers:

```bash
docker ps
```

Open PostgreSQL:

```bash
docker compose exec db psql -U postgres -d tasks
```

View Docker volumes:

```bash
docker volume ls
```

---

## HTTP Status Codes

| Status            | Meaning                   |
| ----------------- | ------------------------- |
| `200 OK`          | Successful read/update    |
| `201 Created`     | Task successfully created |
| `204 No Content`  | Task successfully deleted |
| `400 Bad Request` | Invalid request           |
| `404 Not Found`   | Task does not exist       |

---

## Author

Saim Iftikhar

Built for the FlyRank Backend AI Engineering Internship.



