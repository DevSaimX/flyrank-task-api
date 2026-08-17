# BE-01 FastAPI CRUD API — Revision Notes

## 1. What I Built

I built a small **in-memory Task CRUD API** using Python 3.10+, FastAPI, Uvicorn, Swagger UI/OpenAPI, Git, and GitHub.

Repository: `https://github.com/DevSaimX/flyrank-task-api`

| CRUD | HTTP Method | Endpoint | Purpose |
|---|---|---|---|
| Create | POST | `/tasks` | Create a new task |
| Read | GET | `/tasks` | Get all tasks |
| Read | GET | `/tasks/{task_id}` | Get one task |
| Update | PUT | `/tasks/{task_id}` | Update title and/or done |
| Delete | DELETE | `/tasks/{task_id}` | Delete a task |

Supporting endpoints:

- `GET /` — API metadata
- `GET /health` — health check
- `/docs` — Swagger UI
- `/openapi.json` — OpenAPI schema

---

## 2. Core Backend Mental Model

```text
Client
  |
  | HTTP request
  v
Uvicorn
  |
  v
FastAPI route
  |
  v
Validation + business logic
  |
  v
Application state
  |
  v
HTTP response
  |
  v
Client
```

Examples of clients include a browser, React frontend, mobile app, curl, Postman, Swagger UI, or another backend service.

For this project, data was stored in RAM:

```python
tasks = [
    {"id": 1, "title": "Learn FastAPI basics", "done": False},
    {"id": 2, "title": "Build CRUD API", "done": False},
    {"id": 3, "title": "Test API endpoints", "done": True},
]
```

Because this is in-memory storage, any newly created, updated, or deleted tasks disappear after the server restarts.

---

## 3. FastAPI vs Uvicorn

### FastAPI
FastAPI is the web framework. It defines routes, request parsing, validation, response serialization, and OpenAPI documentation.

```python
@app.get("/tasks")
def get_tasks():
    return tasks
```

### Uvicorn
Uvicorn is the ASGI server. It listens on a port, receives HTTP requests, passes them to FastAPI, and sends the resulting response back.

Run command:

```powershell
python -m uvicorn main:app --reload
```

Meaning:

```text
main      -> load main.py
app       -> use the FastAPI instance named app
--reload  -> restart automatically when source files change
```

---

## 4. What Is an Endpoint?

An endpoint is:

```text
HTTP METHOD + PATH
```

Therefore these are different endpoints:

```text
GET  /tasks
POST /tasks
```

And these are different operations on one resource:

```text
GET    /tasks/1
PUT    /tasks/1
DELETE /tasks/1
```

---

## 5. HTTP Request Structure

Example:

```http
POST /tasks HTTP/1.1
Content-Type: application/json

{"title":"Buy milk"}
```

A request has:

```text
Method  -> POST
Path    -> /tasks
Headers -> Content-Type: application/json
Body    -> {"title":"Buy milk"}
```

`Content-Type: application/json` tells the server to interpret the body as JSON.

---

## 6. HTTP Response Structure

Example:

```http
HTTP/1.1 201 Created
content-type: application/json
content-length: 41

{"id":4,"title":"Buy milk","done":false}
```

A response contains:

1. Status line
2. Headers
3. Blank line
4. Response body

Important headers seen during the project:

```text
server: uvicorn
content-type: application/json
content-length: ...
```

---

## 7. Serialization and Deserialization

### Deserialization
The client sends JSON:

```json
{"title":"Buy milk"}
```

FastAPI parses it into Python data:

```python
{"title": "Buy milk"}
```

### Serialization
Python returns:

```python
{"id": 4, "title": "Buy milk", "done": False}
```

FastAPI converts it to JSON:

```json
{"id":4,"title":"Buy milk","done":false}
```

Remember:

```text
Python -> True / False
JSON   -> true / false
```

---

## 8. CRUD Explained

### Create — POST `/tasks`

Request:

```json
{"title":"Buy milk"}
```

Server:

1. validates the title
2. generates the next ID
3. sets `done=False`
4. appends the task to the list
5. returns the created task

Success:

```text
201 Created
```

### Read All — GET `/tasks`

Returns the complete task collection.

Success:

```text
200 OK
```

### Read One — GET `/tasks/{task_id}`

Example:

```text
GET /tasks/2
```

FastAPI extracts `2` from the URL and converts it based on:

```python
def get_task(task_id: int):
```

### Update — PUT `/tasks/{task_id}`

Examples:

```json
{"done":true}
```

```json
{"title":"Master FastAPI"}
```

```json
{"title":"Master FastAPI","done":true}
```

The assignment used PUT with partial-update behavior. Strict REST conventions often use PATCH for partial updates, but the assignment specifically requested PUT.

### Delete — DELETE `/tasks/{task_id}`

Successful deletion returns:

```text
204 No Content
```

A `204` response must not contain a response body.

---

## 9. Status Codes I Learned

### 200 OK
Used for normal successful reads and updates.

Examples:

```text
GET /tasks
GET /tasks/1
PUT /tasks/1
```

### 201 Created
Used when a new resource was successfully created.

```text
POST /tasks
```

### 204 No Content
Used for a successful operation that intentionally returns no body.

```text
DELETE /tasks/1
```

### 400 Bad Request
Used when the request is understood but violates our API's validation/business rules.

Examples:

```json
{}
```

```json
{"title":""}
```

```json
{"title":"   "}
```

```json
{"done":"yes"}
```

### 404 Not Found
The requested resource does not exist.

Example:

```text
GET /tasks/99
```

Response:

```json
{"error":"Task 99 not found"}
```

A 404 does not mean the server crashed. The server worked, but the requested resource was missing.

### 405 Method Not Allowed
The path exists, but that HTTP method is not registered.

Example:

```text
GET /tasks/1 -> exists
PUT /tasks/1 -> route not registered yet
```

Then PUT can return:

```text
405 Method Not Allowed
Allow: GET
```

### 422 Validation / Unprocessable Content
FastAPI can reject a request before the route's business logic executes.

Examples:

- `/tasks/abc` when `task_id` must be `int`
- malformed JSON
- JSON decoding errors caused by shell quoting

Key distinction:

```text
Malformed or framework-invalid input
        -> FastAPI rejects it
        -> often 422

Valid JSON, but violates our own business rule
        -> route executes
        -> 400
```

---

## 10. Why `JSONResponse` Was Used

FastAPI commonly uses:

```python
raise HTTPException(status_code=404, detail="Task not found")
```

That produces:

```json
{"detail":"Task not found"}
```

The assignment required an `error` field:

```json
{"error":"Task 99 not found"}
```

So I used:

```python
return JSONResponse(
    status_code=404,
    content={"error": f"Task {task_id} not found"},
)
```

This gives precise control over both the HTTP status and JSON body.

---

## 11. Why Manual Body Validation Was Used

Production FastAPI commonly uses Pydantic models:

```python
class TaskCreate(BaseModel):
    title: str
```

That is a strong approach because it provides typed schemas, automatic validation, and better Swagger documentation.

However, default FastAPI validation commonly returns 422. This assignment explicitly required missing or empty titles to return 400, so I used:

```python
payload: dict | None = Body(default=None)
```

and performed validation manually.

A future production version should move toward:

```text
Pydantic schemas
+
custom exception/validation handlers
```

---

## 12. Why `.get("title")` Was Useful

This can raise a `KeyError`:

```python
payload["title"]
```

if the key does not exist.

This safely returns `None`:

```python
payload.get("title")
```

That lets the API respond with a controlled 400 instead of crashing.

---

## 13. Why `.strip()` Matters

This value:

```json
{"title":"     "}
```

is technically a string, but not a useful title.

```python
"     ".strip()
```

becomes an empty string, so validation can reject whitespace-only input.

---

## 14. Why `"done" in payload` Matters

This is an important backend/Python lesson.

Bad check:

```python
if payload.get("done"):
```

If the client sends:

```json
{"done":false}
```

the value is falsy, so the code may incorrectly behave as though `done` was not supplied.

Correct:

```python
has_done = "done" in payload
```

This checks field presence rather than truthiness.

---

## 15. In-Memory State and Mutation

The task list exists inside the Python process.

Create:

```python
tasks.append(new_task)
```

Update:

```python
task["done"] = True
```

Delete:

```python
tasks.pop(index)
```

These operations mutate the running application's state.

After a restart:

```text
process stops
    ->
RAM state disappears
    ->
main.py runs again
    ->
seed tasks return
```

This demonstrates why databases are needed for persistence.

---

## 16. Task ID vs List Index

Never confuse an ID with a list index.

Initially:

```text
index 0 -> id 1
index 1 -> id 2
index 2 -> id 3
```

After deleting ID 2:

```text
index 0 -> id 1
index 1 -> id 3
```

The task with ID 3 remains ID 3.

```text
ID    = resource identity
index = current position in the list
```

---

## 17. Why `max(id) + 1` Was Better Than `len(tasks) + 1`

Suppose IDs are:

```text
1, 3, 4
```

There are three tasks.

This would produce:

```python
len(tasks) + 1
```

which equals 4, but ID 4 already exists.

Instead:

```python
next_id = max(
    (task["id"] for task in tasks),
    default=0,
) + 1
```

produces 5.

In production, the database normally generates IDs through sequences, identity columns, UUIDs, or other strategies.

---

## 18. Why `enumerate()` Was Used for Delete

Normal iteration:

```python
for task in tasks:
```

gives the task.

For deletion from a Python list, I also needed its position:

```python
for index, task in enumerate(tasks):
```

Then:

```python
tasks.pop(index)
```

removes the matching item.

---

## 19. Idempotency

An operation is idempotent when repeating it produces the same final state.

### PUT

Sending:

```json
{"done":true}
```

multiple times still leaves:

```text
done = true
```

### DELETE

Deleting the same resource repeatedly still leaves the final state:

```text
resource does not exist
```

The later response may become 404, but the final state remains unchanged.

### POST

Repeated POST requests can create multiple different resources, so POST is usually not idempotent.

Typical summary:

```text
GET     idempotent
PUT     idempotent
DELETE  idempotent
POST    usually not idempotent
```

---

## 20. Swagger UI and OpenAPI

FastAPI generates documentation automatically:

```text
Python route definitions
        ->
OpenAPI schema
        ->
/openapi.json
        ->
Swagger UI
        ->
/docs
```

### OpenAPI
Machine-readable description of the API.

### Swagger UI
Interactive browser interface that reads the OpenAPI schema.

Swagger's **Try it out** sends real HTTP requests. It is a real API client, just like curl.

---

## 21. Health Endpoint

```text
GET /health
```

Response:

```json
{"status":"ok"}
```

Infrastructure can call this to determine whether the service is alive.

More advanced systems often distinguish:

```text
Liveness  -> Is the process alive?
Readiness -> Can the application actually serve traffic?
```

An API process can be alive while an important dependency such as PostgreSQL is unavailable.

---

## 22. PowerShell + curl Lesson

Windows PowerShell quoting caused malformed JSON during testing.

A reliable pattern was:

```powershell
'{"title":"Buy milk"}' | curl.exe -i -X POST http://localhost:8000/tasks `
  -H "Content-Type: application/json" `
  --data-binary "@-"
```

`@-` tells curl to read the request body from standard input.

Flow:

```text
PowerShell JSON
      ->
pipe
      ->
curl
      ->
HTTP request body
      ->
FastAPI
```

---

## 23. Git Workflow Practiced

The project was developed incrementally:

```text
Stage 0: hello server
Stage 1: root and health endpoints
Stage 2: read endpoints with 404
Stage 3: create with validation
Stage 4: full CRUD
Stage 5: Swagger UI
Stage 6: publish and docs
```

Good workflow:

```text
change code
   ->
test
   ->
git status
   ->
git diff
   ->
git add
   ->
git commit
   ->
git push
```

A commit should represent a meaningful working checkpoint.

---

## 24. Virtual Environment

The project used:

```text
.venu/
```

Activate on PowerShell:

```powershell
.\.venu\Scripts\Activate.ps1
```

Check active Python:

```powershell
where.exe python
```

The first result should point into the project's `.venu`.

Using:

```powershell
python -m pip
```

helps ensure pip belongs to the currently selected Python interpreter.

---

## 25. `.gitignore`

Important ignored files:

```gitignore
.venu/
__pycache__/
*.pyc
*.pyo
*.pyd
.env
notes.txt
```

Reasons:

```text
.venu/       -> local reproducible environment
__pycache__/ -> generated Python cache
*.pyc        -> compiled/generated files
.env         -> can contain secrets
notes.txt    -> personal notes
```

---

## 26. How to Rebuild This Backend From Scratch

### Step 1 — Setup

```powershell
mkdir flyrank-task-api
cd flyrank-task-api
python -m venv .venu
.\.venu\Scripts\Activate.ps1
python -m pip install fastapi "uvicorn[standard]"
```

### Step 2 — Build a hello route

```python
from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def root():
    return {"message": "Hello, server!"}
```

Run:

```powershell
python -m uvicorn main:app --reload
```

### Step 3 — Add `/health`

Confirm the API can expose more than one route.

### Step 4 — Create seed task data

Use a list of dictionaries.

### Step 5 — Add reads

```text
GET /tasks
GET /tasks/{task_id}
```

Add custom 404 behavior.

### Step 6 — Add create

```text
POST /tasks
```

Validate input, generate an ID, append to state, and return 201.

### Step 7 — Add update

```text
PUT /tasks/{task_id}
```

Validate supplied fields and mutate the existing task.

### Step 8 — Add delete

```text
DELETE /tasks/{task_id}
```

Remove the matching task and return 204.

### Step 9 — Test failures

Do not only test the happy path.

Test:

```text
unknown task
missing title
empty title
wrong type
invalid task_id
malformed JSON
unsupported method
delete missing resource
```

### Step 10 — Test in Swagger

Open:

```text
http://localhost:8000/docs
```

Run the complete CRUD cycle using **Try it out**.

### Step 11 — Document and publish

Add:

```text
README.md
requirements.txt
Swagger screenshot
```

and push to a public GitHub repository.

---

## 27. Backend Debugging Decision Tree

When a request fails, check in this order.

### 1. Is the server running?

If not, you may see connection refused.

### 2. Does the path exist?

If not:

```text
404
```

### 3. Is this HTTP method registered for that path?

If not:

```text
405
```

### 4. Is the path parameter valid?

Example:

```text
/tasks/abc
```

for `task_id: int` can produce a FastAPI validation response.

### 5. Is the JSON syntactically valid?

Malformed JSON can fail before route logic executes.

### 6. Is the JSON valid but against business rules?

Example:

```json
{"title":""}
```

Return 400.

### 7. Does the target resource exist?

Example:

```text
/tasks/99
```

Return 404.

This decision tree makes API debugging much faster.

---

## 28. What a Production Version Would Add

This project was intentionally small. A production backend would likely add:

- Pydantic request/response schemas
- PostgreSQL or another persistent database
- SQLAlchemy or another data-access layer
- Alembic migrations
- pytest + HTTPX/TestClient automated tests
- routers/services/repositories architecture
- authentication and authorization
- structured logging
- pagination
- filtering and sorting
- centralized exception handling
- environment-based configuration
- production server/deployment setup

Possible project structure:

```text
app/
├── main.py
├── routers/
├── schemas/
├── models/
├── services/
├── repositories/
├── database/
└── tests/
```

---

## 29. Core Lessons to Remember

1. **Method + path defines an API endpoint.**
2. HTTP status codes communicate machine-readable meaning.
3. `400`, `404`, `405`, and `422` describe different failure classes.
4. Never blindly trust client input.
5. IDs and list indexes are different concepts.
6. Check field presence separately from truthiness when `False` is valid.
7. A `204` response must contain no body.
8. POST creates, GET reads, PUT updates, DELETE removes.
9. Swagger UI sends real HTTP requests.
10. In-memory state is temporary.
11. Databases provide persistence.
12. Good backend testing includes failure paths.
13. Git commits should represent meaningful working states.
14. Backend correctness is largely about controlling inputs, state transitions, outputs, and failures.

---

## 30. Quick Revision Quiz

Try answering these without looking at the notes.

### HTTP
1. What makes `GET /tasks` different from `POST /tasks`?
2. What does `Content-Type: application/json` mean?
3. What are the main parts of an HTTP request?
4. What are the main parts of an HTTP response?

### Status Codes
5. When should an API return 200?
6. Why does create return 201?
7. Why does delete return 204?
8. What is the difference between 404 and 405?
9. What caused the 422 errors during development?
10. When should our own application return 400?

### Python / Backend
11. Why use `payload.get("title")`?
12. Why use `"done" in payload` rather than `if payload.get("done")`?
13. Why should IDs not be treated as list indexes?
14. Why use `max(id) + 1` instead of `len(tasks) + 1`?
15. What happens to in-memory tasks after a server restart?
16. What does `tasks.append(new_task)` do?

### FastAPI
17. What does `@app.get("/tasks")` do?
18. What does `task_id: int` tell FastAPI?
19. What is the difference between FastAPI and Uvicorn?
20. What is OpenAPI?
21. What is Swagger UI?

If I can answer these comfortably, I understand the foundation instead of merely remembering the code.

---

## 31. Is This Worth Posting on LinkedIn?

Yes — but position it as a **backend engineering learning milestone**, not as a large production system.

The value is not simply:

> I made CRUD.

The stronger story is:

> I deliberately learned HTTP behavior, validation, state mutation, failure cases, API documentation, debugging, and incremental Git development.

### Suggested LinkedIn Post

Built and shipped my first FastAPI CRUD API as part of my Backend AI Engineering internship journey.

The implementation is intentionally small, but I used it to go deeper into the backend fundamentals that larger systems depend on:

- HTTP methods and REST-style resource design
- request bodies, path parameters, and JSON serialization
- correct `200`, `201`, `204`, `400`, `404`, `405`, and `422` behavior
- input validation and custom API errors
- in-memory state and why persistence requires a database
- Swagger/OpenAPI for interactive API documentation
- incremental Git development from a hello server to full CRUD

One of the most useful parts was debugging failure paths instead of only testing successful requests. Seeing the practical difference between a missing resource (`404`), unsupported method (`405`), framework/input validation (`422`), and application validation (`400`) made HTTP behavior much clearer.

Next step: moving from in-memory state toward database-backed APIs and stronger schema validation.

GitHub: https://github.com/DevSaimX/flyrank-task-api

#BackendEngineering #FastAPI #Python #RESTAPI #SoftwareEngineering #LearningInPublic

### Best Visual for the Post

Use the Swagger UI screenshot because it immediately shows the API's GET, POST, PUT, and DELETE operations.

An optional second image can show the staged Git progression:

```text
Stage 0 -> Stage 1 -> Stage 2 -> Stage 3 -> Stage 4 -> Stage 5 -> Stage 6
```

---

## 32. One-Sentence Memory Hook

> **A backend API receives an HTTP request, validates the input, performs logic against application state, and returns a response whose status code and body accurately describe what happened.**

That sentence captures the main lesson of this project.
