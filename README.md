# Task API

A FastAPI backend project built during the FlyRank Backend AI Engineering Internship.

The project progressed through multiple assignments while keeping the same core Task API and gradually adding persistence, Docker, PostgreSQL, and authentication.

---

## ✅ BE-01 — FastAPI CRUD — COMPLETED

Built the initial Task API with in-memory Python storage.

### Completed
- `GET /tasks`
- `GET /tasks/{task_id}`
- `POST /tasks`
- `PUT /tasks/{task_id}`
- `DELETE /tasks/{task_id}`
- Validation and correct HTTP status codes
- Swagger UI / OpenAPI documentation

---

## ✅ BE-02 — SQLite Persistence — COMPLETED

Migrated task storage from Python memory to SQLite.

### Completed
- SQLite database integration
- Automatic `tasks` table creation
- Seed data
- Parameterized SQL queries
- Persistent task data after server restart
- Database logic separated into `repository.py`

---

## ✅ BE-04 — PostgreSQL + Docker — COMPLETED

Migrated the storage layer from SQLite to PostgreSQL and containerized the stack.

### Completed
- PostgreSQL 17
- Psycopg 3
- Dockerfile
- Docker Compose
- PostgreSQL Docker volume
- `.env` configuration
- `.env.example`
- Repository layer for database operations
- Persistent data after container restart

### Architecture

```text
FastAPI
   |
   v
repository.py
   |
   v
PostgreSQL
   |
   v
Docker Volume
```

---

## ✅ BE-03 — Supabase Authentication — COMPLETED

Added user authentication and protected routes with Supabase Auth.

### Completed
- `POST /auth/signup`
- `POST /auth/login`
- `POST /auth/logout`
- `GET /public/info`
- `GET /protected/profile`
- `GET /protected/dashboard`
- JWT Bearer authentication
- Supabase token verification
- Reusable FastAPI auth dependency
- Swagger Authorize button and protected-route locks

### Authentication Flow

```text
Signup / Login
      |
      v
Supabase Auth
      |
      v
Access Token
      |
      v
Bearer Authentication
      |
      v
Protected Routes
```

---

## Current Tech Stack

- Python 3.10+
- FastAPI
- Uvicorn
- PostgreSQL 17
- Psycopg 3
- Supabase Auth
- python-dotenv
- Docker
- Docker Compose
- Swagger UI / OpenAPI

---

## Environment Variables

Create `.env` from `.env.example`.

```env
POSTGRES_USER=postgres
POSTGRES_PASSWORD=YOUR_PASSWORD
POSTGRES_DB=tasks
DATABASE_URL=postgresql://postgres:YOUR_PASSWORD@127.0.0.1:5432/tasks

SUPABASE_URL=https://YOUR_PROJECT_REF.supabase.co
SUPABASE_KEY=YOUR_SUPABASE_PUBLISHABLE_KEY

PORT=8000
```

Never commit the real `.env` file.

---

## Run the Project

Start PostgreSQL:

```powershell
docker compose up -d db
```

Activate the virtual environment:

```powershell
.\.venu\Scripts\Activate.ps1
```

Install dependencies:

```powershell
python -m pip install -r requirements.txt
```

Start FastAPI:

```powershell
python -m uvicorn main:app --reload
```

API:

```text
http://127.0.0.1:8000
```

Swagger UI:

```text
http://127.0.0.1:8000/docs
```

---

## Main Endpoints

| Method | Endpoint | Auth |
|---|---|---|
| GET | `/` | No |
| GET | `/health` | No |
| POST | `/auth/signup` | No |
| POST | `/auth/login` | No |
| POST | `/auth/logout` | Bearer |
| GET | `/public/info` | No |
| GET | `/protected/profile` | Bearer |
| GET | `/protected/dashboard` | Bearer |
| GET | `/tasks` | No |
| GET | `/tasks/{task_id}` | No |
| POST | `/tasks` | No |
| PUT | `/tasks/{task_id}` | No |
| DELETE | `/tasks/{task_id}` | No |

---

## Screenshots

### PostgreSQL + Docker

![PostgreSQL Docker Database](docs/postgres-docker.png)

### Supabase Bearer Authentication

![Swagger Bearer Authentication](docs/auth-swagger.png)

---

## Security

- `.env` is excluded from Git.
- `.env.example` contains placeholders only.
- Supabase publishable key is used.
- Supabase service-role key is not used.
- Protected endpoints verify access tokens with Supabase.
- Authentication logic is reused through a FastAPI dependency.

---

## Author

**Saim Iftikhar**

FlyRank Backend AI Engineering Internship
