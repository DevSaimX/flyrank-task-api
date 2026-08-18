Yes — create a new file:

```text
docs/BE-02_SQLite_CRUD_Revision_Notes.md
```

Paste the following entire content into it. It is written as the natural continuation of your BE-01 notes and covers the concepts required by the SQLite assignment. The assignment’s central idea is that the API contract stays the same while the storage layer moves from memory to SQLite. 

````md
# BE-02 SQLite CRUD API — Revision Notes

## 1. What I Built

I upgraded my existing FastAPI Task CRUD API from in-memory storage to a real SQLite database.

Repository:

https://github.com/DevSaimX/flyrank-task-api

The API still exposes the same CRUD endpoints:

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
- `/openapi.json` — OpenAPI specification

The major change from BE-01 was the storage layer.

Before:

```text
Client
   ↓
FastAPI
   ↓
Python List
   ↓
RAM
````

Now:

```text
Client
   ↓
FastAPI
   ↓
SQL Queries
   ↓
SQLite
   ↓
tasks.db
```

The client still uses the same API.

Only the internal data storage changed.

---

## 2. Main Lesson of BE-02

The most important lesson is:

> The API describes what the application does. The database determines where the application stores its data.

In BE-01:

```text
GET /tasks
POST /tasks
PUT /tasks/{id}
DELETE /tasks/{id}
```

worked against a Python list.

In BE-02, those exact same endpoints work against SQLite.

That means the storage layer is an implementation detail behind the API contract.

---

## 3. BE-01 vs BE-02

### BE-01

Storage:

```python
tasks = [
    {
        "id": 1,
        "title": "Learn FastAPI basics",
        "done": False,
    }
]
```

Tasks lived in RAM.

If the server stopped:

```text
Python process stops
        ↓
RAM state disappears
        ↓
created tasks disappear
```

### BE-02

Storage:

```text
tasks.db
```

Tasks live on disk.

If the server stops:

```text
Python process stops
        ↓
RAM disappears
        ↓
tasks.db remains
        ↓
server restarts
        ↓
tasks are still available
```

This property is called persistence.

---

## 4. What Is a Database?

A database stores structured information so that the data can survive after the application stops.

In this project:

```text
Database file:
tasks.db
```

Inside the database:

```text
tasks table
```

Inside the table:

```text
rows
```

Each row represents one task.

Example:

```text
id | title                  | done
---|------------------------|-----
1  | Learn FastAPI basics   | 0
2  | Build CRUD API         | 0
3  | Test API endpoints     | 1
```

---

## 5. What Is SQLite?

SQLite is a lightweight relational database.

Unlike PostgreSQL or MySQL, SQLite does not require a separate database server.

The entire database can exist as one file:

```text
tasks.db
```

Architecture:

```text
FastAPI
   ↓
Python sqlite3
   ↓
tasks.db
```

Advantages for this project:

* no separate database server
* no account required
* no database installation required
* single database file
* supports SQL
* persistent storage
* included with Python through `sqlite3`

---

## 6. Why SQLite Was Chosen

SQLite is ideal for this assignment because it makes it possible to learn real database concepts without adding infrastructure complexity.

It provides:

* tables
* rows
* columns
* primary keys
* SQL queries
* persistent storage
* parameterized queries

while still being simple enough to use locally.

For larger production applications, databases such as PostgreSQL are more common, but the SQL and persistence concepts learned here transfer directly.

---

## 7. Python `sqlite3`

Python includes SQLite support through:

```python
import sqlite3
```

No extra package is required.

A connection can be opened with:

```python
sqlite3.connect("tasks.db")
```

If `tasks.db` does not exist, SQLite creates it.

If it already exists, SQLite opens the existing database.

Conceptually:

```text
sqlite3.connect("tasks.db")
        ↓
Does tasks.db exist?
        ↓
Yes → open it
No  → create it, then open it
```

---

## 8. Database Configuration

The project defines:

```python
DATABASE_NAME = "tasks.db"
```

This keeps the database filename in one place.

Instead of writing:

```python
sqlite3.connect("tasks.db")
```

everywhere, the application can use the constant.

---

## 9. Database Connection Helper

The project uses a helper:

```python
def get_connection():
    connection = sqlite3.connect(DATABASE_NAME)
    connection.row_factory = sqlite3.Row
    return connection
```

Purpose:

```text
Open connection
      ↓
configure rows
      ↓
return connection
```

This avoids repeating the connection setup inside every endpoint.

---

## 10. What Is a Database Connection?

A database connection is the communication channel between Python and SQLite.

Conceptually:

```text
FastAPI / Python
      ↓
database connection
      ↓
SQLite
      ↓
tasks.db
```

Python sends SQL commands through this connection.

For example:

```python
connection.execute(
    "SELECT * FROM tasks"
)
```

means:

> SQLite, execute this SQL query against the database.

---

## 11. `sqlite3.Row`

Normally SQLite may return a row like:

```python
(1, "Learn FastAPI basics", 0)
```

That means:

```text
row[0] → id
row[1] → title
row[2] → done
```

The project configures:

```python
connection.row_factory = sqlite3.Row
```

Now columns can be accessed by name:

```python
row["id"]
row["title"]
row["done"]
```

This is clearer and less error-prone.

---

## 12. Database Schema

The database contains a table named:

```text
tasks
```

Its schema is:

```sql
CREATE TABLE IF NOT EXISTS tasks (
    id INTEGER PRIMARY KEY,
    title TEXT NOT NULL,
    done INTEGER NOT NULL DEFAULT 0
);
```

Columns:

| Column  | Meaning                |
| ------- | ---------------------- |
| `id`    | Unique task identifier |
| `title` | Task title             |
| `done`  | Completion state       |

---

## 13. What Is a Table?

A table is a structured collection of related records.

Example:

```text
tasks
```

contains task records.

Think of a table like a spreadsheet:

```text
id | title | done
```

except a relational database provides stronger structure, querying, constraints, and persistence.

---

## 14. What Is a Row?

A row is one record.

Example:

```text
4 | Buy milk | 0
```

represents one task:

```json
{
  "id": 4,
  "title": "Buy milk",
  "done": false
}
```

---

## 15. What Is a Column?

A column represents one property stored for each record.

This project's columns are:

```text
id
title
done
```

Example:

```text
title = "Buy milk"
```

---

## 16. What Is a Primary Key?

The schema uses:

```sql
id INTEGER PRIMARY KEY
```

A primary key uniquely identifies every row.

Example:

```text
id = 1
id = 2
id = 3
```

Two rows cannot have the same primary-key value.

The API uses the primary key in endpoints such as:

```text
GET /tasks/2
PUT /tasks/2
DELETE /tasks/2
```

---

## 17. SQLite Generates IDs

In BE-01, Python generated IDs manually.

Example:

```python
next_id = max(
    (task["id"] for task in tasks),
    default=0,
) + 1
```

In BE-02, SQLite generates the ID.

The INSERT query does not include `id`:

```sql
INSERT INTO tasks (title, done)
VALUES (?, ?);
```

SQLite assigns the primary key.

Python can retrieve it through:

```python
cursor.lastrowid
```

This is an important shift:

```text
BE-01:
Python manages IDs

BE-02:
Database manages IDs
```

---

## 18. Important SQLite ID Behavior

The schema uses:

```sql
id INTEGER PRIMARY KEY
```

During testing, task ID 4 was deleted.

The next inserted task received ID 4 again.

This can happen because the schema does not use:

```sql
AUTOINCREMENT
```

For this assignment, that is acceptable.

The requirement is that IDs uniquely identify current rows, not that deleted IDs can never be reused.

---

## 19. Why `title` Uses `TEXT NOT NULL`

The schema contains:

```sql
title TEXT NOT NULL
```

`TEXT` means the column stores text.

`NOT NULL` means the database does not allow:

```text
title = NULL
```

This is a database-level constraint.

The API still performs its own validation because database constraints and API validation solve different problems.

---

## 20. Why `done` Uses INTEGER

The schema stores:

```sql
done INTEGER NOT NULL DEFAULT 0
```

SQLite stores the task state as:

```text
0 → false
1 → true
```

The API exposes:

```json
false
```

and:

```json
true
```

So the conversion is:

```text
SQLite   Python   JSON
0        False    false
1        True     true
```

---

## 21. Row Conversion

The project uses:

```python
def row_to_task(row):
    return {
        "id": row["id"],
        "title": row["title"],
        "done": bool(row["done"]),
    }
```

Purpose:

```text
SQLite row
     ↓
Python dictionary
     ↓
FastAPI
     ↓
JSON
```

For example:

```text
SQLite:
4 | Buy milk | 0
```

becomes:

```python
{
    "id": 4,
    "title": "Buy milk",
    "done": False,
}
```

FastAPI serializes this as:

```json
{
  "id": 4,
  "title": "Buy milk",
  "done": false
}
```

---

## 22. Automatic Database Initialization

The project uses an initialization function.

Conceptually:

```text
Application starts
      ↓
open tasks.db
      ↓
create tasks table if needed
      ↓
count rows
      ↓
if table is empty
      ↓
insert three seed tasks
```

This means a user cloning the repository does not need to manually create the database.

Running the application creates the required storage automatically.

---

## 23. `CREATE TABLE IF NOT EXISTS`

The project executes:

```sql
CREATE TABLE IF NOT EXISTS tasks (
    id INTEGER PRIMARY KEY,
    title TEXT NOT NULL,
    done INTEGER NOT NULL DEFAULT 0
);
```

`IF NOT EXISTS` is important.

Without it:

```text
first startup
→ create tasks table

second startup
→ try to create tasks again
→ error
```

With it:

```text
first startup
→ table does not exist
→ create it

second startup
→ table already exists
→ leave it alone
```

This makes initialization safe to repeat.

---

## 24. Seed Data

The application starts with three example tasks.

Before inserting them, it runs:

```sql
SELECT COUNT(*) FROM tasks;
```

Python gets the number of existing rows.

If:

```text
row count = 0
```

the seed tasks are inserted.

If:

```text
row count > 0
```

nothing is inserted.

This prevents:

```text
restart 1 → 3 tasks
restart 2 → 6 tasks
restart 3 → 9 tasks
```

Instead:

```text
restart 1 → 3 tasks
restart 2 → 3 tasks
restart 3 → 3 tasks
```

Important nuance:

The code checks whether the table is empty at startup.

Therefore, if every row is manually deleted and the application is later restarted, the three seed tasks can be inserted again.

---

## 25. `SELECT COUNT(*)`

This query:

```sql
SELECT COUNT(*) FROM tasks;
```

counts rows.

Example:

```text
3
```

means there are three tasks.

Python retrieves the value using:

```python
connection.execute(
    "SELECT COUNT(*) FROM tasks"
).fetchone()[0]
```

---

## 26. What Is SQL?

SQL means Structured Query Language.

It is used to interact with relational databases.

The four main operations in this project are:

```text
SELECT
INSERT
UPDATE
DELETE
```

These map directly to CRUD:

```text
Create → INSERT
Read   → SELECT
Update → UPDATE
Delete → DELETE
```

---

## 27. CRUD to SQL Mapping

| CRUD   | HTTP   | SQL    |
| ------ | ------ | ------ |
| Create | POST   | INSERT |
| Read   | GET    | SELECT |
| Update | PUT    | UPDATE |
| Delete | DELETE | DELETE |

This mapping is one of the most important patterns to remember.

---

## 28. GET `/tasks`

The API runs:

```sql
SELECT * FROM tasks;
```

Meaning:

```text
SELECT
→ read data

*
→ all columns

FROM tasks
→ from the tasks table
```

Python:

```python
rows = connection.execute(
    "SELECT * FROM tasks"
).fetchall()
```

Then:

```python
return [
    row_to_task(row)
    for row in rows
]
```

---

## 29. `.fetchall()`

When a query may return several rows:

```python
.fetchall()
```

retrieves them all.

Example:

```sql
SELECT * FROM tasks;
```

may return:

```text
row 1
row 2
row 3
row 4
```

Therefore:

```python
.fetchall()
```

is appropriate.

Memory hook:

```text
many rows → fetchall()
```

---

## 30. GET `/tasks/{task_id}`

The API uses:

```sql
SELECT *
FROM tasks
WHERE id = ?;
```

Example request:

```text
GET /tasks/2
```

FastAPI gives:

```python
task_id = 2
```

SQLite receives:

```text
SQL:
SELECT * FROM tasks WHERE id = ?

Parameter:
2
```

It finds the row whose ID is 2.

---

## 31. `.fetchone()`

For a query expected to return one row:

```python
.fetchone()
```

is used.

Example:

```python
row = connection.execute(
    "SELECT * FROM tasks WHERE id = ?",
    (task_id,),
).fetchone()
```

If the row exists:

```text
SQLite row
```

is returned.

If nothing matches:

```python
None
```

is returned.

Memory hook:

```text
one row → fetchone()
many rows → fetchall()
```

---

## 32. `WHERE`

`WHERE` filters rows.

Example:

```sql
SELECT *
FROM tasks
WHERE id = 2;
```

means:

> Return rows from tasks where the ID equals 2.

Another example:

```sql
SELECT *
FROM tasks
WHERE done = 1;
```

returns only completed tasks.

---

## 33. Parameterized Queries

The project uses queries such as:

```python
connection.execute(
    "SELECT * FROM tasks WHERE id = ?",
    (task_id,),
)
```

The `?` is a placeholder.

SQL instruction:

```sql
SELECT * FROM tasks WHERE id = ?
```

Value:

```text
task_id
```

are passed separately.

This is called a parameterized query.

---

## 34. Why Parameterized Queries Matter

Bad pattern:

```python
f"SELECT * FROM tasks WHERE id = {task_id}"
```

Even more dangerous with user-controlled strings:

```python
f"SELECT * FROM users WHERE name = '{username}'"
```

Parameterized form:

```python
connection.execute(
    "SELECT * FROM tasks WHERE id = ?",
    (task_id,),
)
```

keeps:

```text
SQL instructions
```

separate from:

```text
user data
```

This helps prevent SQL injection and avoids many quoting problems.

---

## 35. Why `(task_id,)` Has a Comma

In Python:

```python
(task_id)
```

is just the value inside parentheses.

But:

```python
(task_id,)
```

creates a one-item tuple.

Example:

```python
task_id = 4
```

Then:

```python
(task_id,)
```

becomes:

```python
(4,)
```

SQLite expects query parameters as a sequence.

Therefore:

```python
connection.execute(
    "SELECT * FROM tasks WHERE id = ?",
    (task_id,),
)
```

is correct.

---

## 36. POST `/tasks`

The POST endpoint validates the title and then runs:

```sql
INSERT INTO tasks (title, done)
VALUES (?, ?);
```

Example values:

```text
"Buy milk"
0
```

The resulting database row may be:

```text
4 | Buy milk | 0
```

The API returns:

```json
{
  "id": 4,
  "title": "Buy milk",
  "done": false
}
```

with:

```text
201 Created
```

---

## 37. `INSERT INTO`

`INSERT` creates a new row.

General structure:

```sql
INSERT INTO table_name (column1, column2)
VALUES (?, ?);
```

Project example:

```sql
INSERT INTO tasks (title, done)
VALUES (?, ?);
```

This is the SQL equivalent of BE-01's:

```python
tasks.append(new_task)
```

Comparison:

```text
BE-01:
tasks.append()

BE-02:
INSERT INTO
```

---

## 38. `cursor.lastrowid`

After INSERT:

```python
cursor = connection.execute(
    """
    INSERT INTO tasks (title, done)
    VALUES (?, ?)
    """,
    (clean_title, 0),
)
```

SQLite generates the ID.

Python retrieves it using:

```python
new_task_id = cursor.lastrowid
```

Example:

```text
SQLite inserts task ID 4
        ↓
cursor.lastrowid
        ↓
4
```

This lets the API return the newly created task.

---

## 39. Persistence Test

One of the most important tests in this assignment was:

```text
POST /tasks
     ↓
create "Buy milk"
     ↓
GET /tasks
     ↓
Buy milk exists
     ↓
stop Uvicorn
     ↓
start Uvicorn again
     ↓
GET /tasks
     ↓
Buy milk still exists
```

This proved the task was stored in:

```text
tasks.db
```

instead of only RAM.

---

## 40. PUT `/tasks/{task_id}`

The update endpoint supports changing:

```text
title
done
```

or both.

Examples:

```json
{
  "done": true
}
```

```json
{
  "title": "Buy milk and eggs"
}
```

```json
{
  "title": "Buy milk and eggs",
  "done": true
}
```

---

## 41. Why PUT First Reads the Existing Row

The API supports partial update behavior.

Suppose the database contains:

```text
id = 4
title = Buy milk
done = 0
```

The client sends:

```json
{
  "done": true
}
```

The request does not include the title.

The application first executes:

```sql
SELECT *
FROM tasks
WHERE id = ?;
```

so it knows the existing title.

Then it keeps:

```text
title = Buy milk
```

and changes:

```text
done = 1
```

---

## 42. `UPDATE`

The update query is:

```sql
UPDATE tasks
SET title = ?, done = ?
WHERE id = ?;
```

Meaning:

```text
UPDATE tasks
→ modify rows in tasks

SET
→ assign new values

WHERE id = ?
→ only modify the requested task
```

The `WHERE` clause is extremely important.

Without it:

```sql
UPDATE tasks
SET done = 1;
```

every task would be updated.

---

## 43. Update Flow

Full flow:

```text
PUT /tasks/4
      ↓
validate body
      ↓
SELECT existing row
      ↓
task exists?
      ↓
merge existing + supplied values
      ↓
UPDATE tasks
      ↓
SELECT updated row
      ↓
return JSON
```

This preserves the API behavior while moving storage to SQL.

---

## 44. PUT Validation

The API rejects:

```json
{}
```

because at least one field must be provided.

Response:

```text
400 Bad Request
```

Example error:

```json
{
  "error": "At least one field is required"
}
```

It also validates:

```text
title must be non-empty text
done must be boolean
```

Moving to SQLite did not remove the API's validation responsibility.

---

## 45. DELETE `/tasks/{task_id}`

The database deletion uses:

```sql
DELETE FROM tasks
WHERE id = ?;
```

Comparison:

BE-01:

```python
tasks.pop(index)
```

BE-02:

```sql
DELETE FROM tasks
WHERE id = ?;
```

---

## 46. Delete Flow

Conceptually:

```text
DELETE /tasks/4
       ↓
SELECT task
       ↓
does it exist?
       ↓
yes
       ↓
DELETE FROM tasks
       ↓
204 No Content
```

If it does not exist:

```text
404 Not Found
```

---

## 47. Why DELETE Returns 204

Successful delete returns:

```text
204 No Content
```

A 204 response must have no body.

Correct:

```python
return Response(status_code=204)
```

Not:

```json
{
  "message": "deleted"
}
```

because that would violate the meaning of 204.

---

## 48. Complete Database-Backed CRUD Architecture

After Stage 3:

```text
GET /tasks
      ↓
SELECT

GET /tasks/{id}
      ↓
SELECT ... WHERE

POST /tasks
      ↓
INSERT

PUT /tasks/{id}
      ↓
SELECT + UPDATE

DELETE /tasks/{id}
      ↓
SELECT + DELETE

All operations
      ↓
SQLite
      ↓
tasks.db
```

At this point the old Python task list was no longer needed.

SQLite became the single source of truth.

---

## 49. Single Source of Truth

Before the complete migration, the application temporarily had:

```text
Python list
+
SQLite database
```

That was only part of the staged migration.

After Stage 3:

```text
tasks.db
```

became the only storage source.

This avoids inconsistencies such as:

```text
POST writes to list
GET reads database
```

A backend should ideally have one authoritative source for its application data.

---

## 50. Stage-by-Stage Migration

The migration was intentionally performed gradually.

### Stage 0

Create:

```text
tasks.db
```

Create:

```text
tasks table
```

Seed three tasks.

### Stage 1

Move reads:

```text
GET /tasks
GET /tasks/{id}
```

to SQL.

### Stage 2

Move:

```text
POST /tasks
```

to SQL.

### Stage 3

Move:

```text
PUT
DELETE
```

to SQL.

After Stage 3:

```text
all CRUD → SQLite
```

This staged approach made it easier to test each change independently.

---

## 51. Why a Staged Migration Is Useful

Instead of rewriting everything at once:

```text
change all code
      ↓
something breaks
      ↓
hard to identify cause
```

the migration was:

```text
small change
   ↓
test
   ↓
commit
   ↓
next change
```

This reduces debugging complexity.

It is similar to how production backend systems are often migrated incrementally.

---

## 52. Manual SQL with DB Browser

The database was opened directly using DB Browser for SQLite.

This showed that:

```text
FastAPI
```

and:

```text
DB Browser
```

were both accessing the same:

```text
tasks.db
```

There is no separate synchronization step.

Both tools read and write the same database file.

---

## 53. SQL Queries Practiced

### List all tasks

```sql
SELECT * FROM tasks;
```

### Show completed tasks

```sql
SELECT * FROM tasks
WHERE done = 1;
```

### Count tasks

```sql
SELECT COUNT(*) FROM tasks;
```

### Mark every task completed

```sql
UPDATE tasks
SET done = 1;
```

### Delete completed tasks

```sql
DELETE FROM tasks
WHERE done = 1;
```

---

## 54. Important `WHERE` Lesson

Compare:

```sql
UPDATE tasks
SET done = 1;
```

with:

```sql
UPDATE tasks
SET done = 1
WHERE id = 4;
```

First query:

```text
updates every row
```

Second query:

```text
updates one matching row
```

Likewise:

```sql
DELETE FROM tasks;
```

would delete every task.

While:

```sql
DELETE FROM tasks
WHERE id = ?;
```

targets one task.

A missing `WHERE` clause can cause destructive database operations.

---

## 55. What Happened During Stage 4

The queries:

```sql
UPDATE tasks SET done = 1;
```

followed by:

```sql
DELETE FROM tasks WHERE done = 1;
```

caused all rows to be removed.

Why?

First:

```text
every task → done = 1
```

Then:

```text
delete every task where done = 1
```

Therefore:

```text
tasks table → empty
```

This was expected SQL behavior.

---

## 56. API Immediately Reflected Manual SQL Changes

After manually changing the database, calling:

```text
GET /tasks
```

showed the changes.

Flow:

```text
DB Browser
     ↓
modify tasks.db
     ↓
FastAPI GET
     ↓
SELECT from tasks.db
     ↓
new database state appears
```

This demonstrated that SQLite is the application's source of truth.

---

## 57. What Is Persistence?

Persistence means data remains after the program stops.

BE-01:

```text
memory
→ temporary
```

BE-02:

```text
database
→ persistent
```

Persistence test:

```text
create task
   ↓
restart server
   ↓
task remains
```

This is one of the main reasons real applications use databases.

---

## 58. Database File and `.gitignore`

The local database file is:

```text
tasks.db
```

It should normally be ignored by Git.

`.gitignore` includes:

```gitignore
tasks.db
```

Reason:

Each developer or clone should create its own local database.

Expected clean-clone flow:

```text
git clone
    ↓
no tasks.db
    ↓
start FastAPI
    ↓
tasks.db automatically created
    ↓
tasks table automatically created
    ↓
seed tasks inserted
```

---

## 59. Why Not Commit `tasks.db`?

A local database can contain:

* test data
* local state
* generated records
* machine-specific development information

The application already knows how to create the database.

Therefore storing the generated database file in Git is unnecessary for this assignment.

What should be committed is:

```text
main.py
README.md
requirements.txt
screenshots
database initialization code
```

not the generated database file.

---

## 60. Schema vs Data

Schema means:

```text
structure of the database
```

For example:

```text
tasks table
id column
title column
done column
```

Data means:

```text
actual rows stored inside that structure
```

Example:

```text
4 | Buy milk | 0
```

So:

```text
schema = shape
data = contents
```

---

## 61. What Is a Migration?

A migration is a controlled change to the database schema.

Current schema:

```text
id
title
done
```

Suppose later we add:

```text
created_at
```

That changes the table's structure.

In larger applications, a migration tool records and applies these schema changes safely.

Examples include:

```text
Alembic
Django migrations
Prisma migrations
```

This assignment only introduced the concept.

---

## 62. Status Codes Preserved

One goal was to keep BE-01 behavior unchanged.

Important statuses:

### 200 OK

Used for:

```text
GET /tasks
GET /tasks/{id}
PUT /tasks/{id}
```

### 201 Created

Used for:

```text
POST /tasks
```

### 204 No Content

Used for:

```text
DELETE /tasks/{id}
```

### 400 Bad Request

Used for invalid application input.

Examples:

```json
{}
```

```json
{
  "title": ""
}
```

### 404 Not Found

Used when the requested task does not exist.

---

## 63. API Contract

An API contract includes things such as:

```text
endpoint paths
HTTP methods
request bodies
response bodies
status codes
error behavior
```

The BE-02 migration deliberately preserved this contract.

Before:

```text
GET /tasks
```

returned tasks from memory.

After:

```text
GET /tasks
```

returns tasks from SQLite.

From the client's perspective:

```text
nothing changed
```

That is the key architectural lesson.

---

## 64. API Layer vs Data Layer

Think of the project as layers.

### API Layer

Responsible for:

* HTTP endpoints
* request parsing
* validation
* status codes
* response JSON

### Data Layer

Responsible for:

* storing tasks
* retrieving tasks
* updating tasks
* deleting tasks

BE-01 data layer:

```text
Python list
```

BE-02 data layer:

```text
SQLite
```

The API layer remained mostly unchanged.

---

## 65. HTTP Request to Database Flow

Example:

```text
POST /tasks
```

Full flow:

```text
Client
   ↓
HTTP POST /tasks
   ↓
Uvicorn
   ↓
FastAPI
   ↓
create_task()
   ↓
validate JSON
   ↓
SQLite connection
   ↓
INSERT query
   ↓
tasks.db
   ↓
SQLite creates row
   ↓
FastAPI builds response
   ↓
201 Created
   ↓
Client
```

---

## 66. Database Read Flow

Example:

```text
GET /tasks/2
```

Flow:

```text
Client
   ↓
GET /tasks/2
   ↓
FastAPI
   ↓
task_id = 2
   ↓
SELECT * FROM tasks WHERE id = ?
   ↓
SQLite
   ↓
matching row
   ↓
row_to_task()
   ↓
Python dict
   ↓
JSON
   ↓
200 OK
```

---

## 67. Database Update Flow

Example:

```text
PUT /tasks/4
```

Flow:

```text
Client
   ↓
request body
   ↓
FastAPI validates fields
   ↓
SELECT existing task
   ↓
merge existing and new values
   ↓
UPDATE task
   ↓
SELECT updated task
   ↓
return JSON
```

---

## 68. Database Delete Flow

Example:

```text
DELETE /tasks/4
```

Flow:

```text
Client
   ↓
FastAPI
   ↓
SELECT task
   ↓
exists?
   ↓
DELETE FROM tasks WHERE id = ?
   ↓
204 No Content
```

---

## 69. Validation Still Belongs at the API Layer

Using a database does not mean the database should handle every validation rule.

For example:

```json
{
  "title": "    "
}
```

should be rejected before attempting meaningful storage.

The application still validates:

```text
title exists
title is string
title is not whitespace
done is boolean
```

The database provides additional structural constraints.

Good backend systems use multiple layers of protection.

---

## 70. Database Constraints vs API Validation

Database constraint:

```sql
title TEXT NOT NULL
```

prevents null values.

API validation:

```python
if not isinstance(title, str) or not title.strip():
```

prevents:

```text
missing title
empty title
whitespace title
wrong type
```

These are complementary.

---

## 71. Why SQL Is Better Than Looping Through Python Data

BE-01 could search using:

```python
for task in tasks:
    if task["id"] == task_id:
        ...
```

BE-02 asks the database:

```sql
SELECT *
FROM tasks
WHERE id = ?;
```

This moves data operations into the database system.

As applications grow, databases provide:

* indexing
* querying
* transactions
* constraints
* concurrency control
* optimized storage

---

## 72. What Is a Query?

A query is a command sent to a database.

Examples:

```sql
SELECT * FROM tasks;
```

```sql
INSERT INTO tasks (title, done)
VALUES (?, ?);
```

```sql
UPDATE tasks
SET done = ?
WHERE id = ?;
```

```sql
DELETE FROM tasks
WHERE id = ?;
```

Each is one database query.

---

## 73. Transactions — Basic Idea

A transaction groups database operations into a logical unit.

Conceptually:

```text
BEGIN
   operation 1
   operation 2
   operation 3
COMMIT
```

If something goes wrong, a database can often:

```text
ROLLBACK
```

the changes.

The assignment introduces this concept as an optional stretch topic.

For larger backend systems, transactions are essential for keeping related changes consistent.

---

## 74. `with sqlite3.connect(...)`

The application uses:

```python
with sqlite3.connect(DATABASE_NAME) as connection:
```

This provides convenient transaction handling for simple operations.

Conceptually:

```text
open connection
      ↓
execute database work
      ↓
successful exit
      ↓
commit
      ↓
close connection
```

This is convenient for a small SQLite project.

---

## 75. DB Browser for SQLite

DB Browser provides a graphical way to inspect the database.

It was used to:

* open `tasks.db`
* inspect the `tasks` table
* view rows
* execute SQL manually
* modify rows
* verify changes

This helped connect the API code to the actual database contents.

---

## 76. Database Screenshot

The project documentation includes a screenshot showing the SQLite database.

Example path:

```text
docs/sqlite-database.png
```

README:

```md
![SQLite Database](docs/sqlite-database.png)
```

This proves the project is actually using a database and shows the stored rows.

---

## 77. Swagger Still Works

Moving from memory to SQLite does not affect Swagger.

FastAPI still generates:

```text
/openapi.json
```

and:

```text
/docs
```

Swagger sends HTTP requests to the same endpoints.

The database implementation is hidden behind those endpoints.

---

## 78. Why the Same API Tests Still Matter

A powerful way to prove that the storage layer is an implementation detail is to reuse the same endpoint tests from BE-01.

For example:

```text
GET /tasks
POST /tasks
PUT /tasks/{id}
DELETE /tasks/{id}
```

should still behave the same.

If the same tests pass before and after the migration:

```text
API contract preserved
```

while:

```text
internal storage changed
```

This is exactly the separation the assignment is trying to teach.

---

## 79. Git Workflow

The database migration was developed stage by stage.

Required BE-02 commits:

```text
Stage 0: create SQLite database
Stage 1: database read endpoints
Stage 2: insert into database
Stage 3: update and delete with SQL
Stage 4: explored SQLite
Stage 5: database documentation
```

Workflow:

```text
change
   ↓
test
   ↓
git status
   ↓
git diff
   ↓
git add
   ↓
git commit
   ↓
next stage
```

---

## 80. Why One Commit Per Stage Is Useful

Each commit represents one working milestone.

If Stage 3 introduces a problem, the Git history clearly shows:

```text
Stage 2 worked
Stage 3 changed update/delete
```

This makes debugging and code review easier.

Good commits provide a history of how the application evolved.

---

## 81. Project Structure

Example final structure:

```text
flyrank-task-api/
│
├── docs/
│   ├── BE-01_FastAPI_CRUD_Revision_Notes.md
│   ├── BE-02_SQLite_CRUD_Revision_Notes.md
│   ├── swagger-ui.png
│   └── sqlite-database.png
│
├── .gitignore
├── main.py
├── requirements.txt
└── README.md
```

Local generated file:

```text
tasks.db
```

exists in the project directory but is ignored by Git.

---

## 82. Clean Clone Behavior

A stranger should be able to:

```bash
git clone https://github.com/DevSaimX/flyrank-task-api.git
cd flyrank-task-api
```

Create environment:

```powershell
python -m venv .venu
.\.venu\Scripts\Activate.ps1
```

Install dependencies:

```powershell
python -m pip install -r requirements.txt
```

Run:

```powershell
python -m uvicorn main:app --reload
```

Then automatically:

```text
tasks.db created
      ↓
tasks table created
      ↓
seed tasks inserted
      ↓
API ready
```

No manual database setup should be required.

---

## 83. Important Debugging Lesson — Database vs API

When debugging a database-backed API, separate the layers.

Ask:

### 1. Is the server running?

If not:

```text
connection refused
```

### 2. Does the route exist?

If not:

```text
404 / 405 depending on request
```

### 3. Is request validation passing?

If not:

```text
400 / 422
```

### 4. Is SQLite connection working?

Check:

```text
tasks.db
```

### 5. Does the table exist?

Check:

```sql
SELECT * FROM tasks;
```

### 6. Does the requested row exist?

Check:

```sql
SELECT *
FROM tasks
WHERE id = ?;
```

### 7. Did the write commit?

Check through:

```text
GET endpoint
```

or DB Browser.

This layer-by-layer debugging approach is much faster than randomly changing code.

---

## 84. Debugging ID Reuse

During Stage 3 testing:

```text
task 4 was deleted
```

Then a new task was created.

The new task received:

```text
id = 4
```

instead of:

```text
id = 5
```

The important lesson:

Never assume:

```text
next task must be previous highest ID + 1
```

unless the database schema guarantees that behavior.

Instead, always trust the ID returned by the database:

```python
cursor.lastrowid
```

Then use the actual returned ID in later requests.

---

## 85. SQLite Viewer vs VS Code

Opening:

```text
tasks.db
```

in the normal VS Code text editor shows:

```text
binary / unsupported encoding
```

because SQLite databases are binary files.

They should be inspected with:

* DB Browser for SQLite
* a SQLite extension
* the `sqlite3` command line
* application code

not as normal text.

---

## 86. `tasks.db` Is the Database

An important mental model:

```text
tasks.db
```

is not just an export or backup.

It is the actual SQLite database.

When FastAPI writes a task:

```text
SQLite modifies tasks.db
```

When DB Browser edits a task:

```text
DB Browser modifies tasks.db
```

Both applications operate on the same data file.

---

## 87. SQL Safety Habit

Always prefer:

```python
connection.execute(
    "DELETE FROM tasks WHERE id = ?",
    (task_id,),
)
```

over:

```python
connection.execute(
    f"DELETE FROM tasks WHERE id = {task_id}"
)
```

The first keeps SQL and external values separate.

Develop this habit even when the current input seems safe.

Later, inputs may include:

```text
names
emails
search text
usernames
messages
```

Parameterized queries become essential.

---

## 88. What Would a Production Version Change?

This project intentionally uses raw `sqlite3` for learning.

A larger production FastAPI application may use:

* PostgreSQL
* SQLAlchemy
* SQLModel
* Alembic migrations
* Pydantic request/response schemas
* repository layer
* service layer
* dependency injection
* connection pooling
* automated tests
* async database drivers
* authentication
* authorization
* logging
* environment configuration

Possible structure:

```text
app/
├── main.py
├── api/
├── schemas/
├── models/
├── services/
├── repositories/
├── database/
└── tests/
```

The concepts learned in BE-02 still apply.

---

## 89. SQLite vs PostgreSQL

SQLite:

```text
single file
no database server
excellent for local/small applications
simple setup
```

PostgreSQL:

```text
separate database server
better suited for larger multi-user systems
strong concurrency
network-accessible
advanced features
```

The API layer can remain similar while the storage technology changes.

That is another reason learning the separation between API and database is important.

---

## 90. Core Concepts Learned

### Database

Persistent structured data storage.

### SQLite

Single-file relational database.

### Table

Collection of related records.

### Row

One record.

### Column

One property of a record.

### Primary Key

Unique identifier.

### SQL

Language for interacting with relational databases.

### Query

One SQL command.

### Persistence

Data survives process restart.

### Schema

Structure of the database.

### Parameterized Query

SQL with placeholders and values supplied separately.

### Seed Data

Starter rows inserted automatically.

### Migration

Controlled database schema change.

---

## 91. Most Important SQL Commands

### Create table

```sql
CREATE TABLE IF NOT EXISTS tasks (...);
```

### Read

```sql
SELECT * FROM tasks;
```

### Read one

```sql
SELECT *
FROM tasks
WHERE id = ?;
```

### Insert

```sql
INSERT INTO tasks (title, done)
VALUES (?, ?);
```

### Update

```sql
UPDATE tasks
SET title = ?, done = ?
WHERE id = ?;
```

### Delete

```sql
DELETE FROM tasks
WHERE id = ?;
```

### Count

```sql
SELECT COUNT(*) FROM tasks;
```

---

## 92. SQL Memory Hook

Remember:

```text
SELECT = read
INSERT = create
UPDATE = modify
DELETE = remove
WHERE  = choose which rows
```

And:

```text
CRUD   SQL

C      INSERT
R      SELECT
U      UPDATE
D      DELETE
```

---

## 93. API + SQL Memory Hook

```text
POST   → INSERT
GET    → SELECT
PUT    → UPDATE
DELETE → DELETE
```

This pattern appears constantly in backend systems.

---

## 94. BE-01 to BE-02 Evolution

BE-01 taught:

```text
HTTP
FastAPI
routes
validation
CRUD
status codes
Swagger
in-memory state
```

BE-02 added:

```text
databases
SQLite
SQL
persistence
tables
rows
columns
primary keys
parameterized queries
database-generated IDs
database initialization
```

Together:

```text
Client
   ↓
HTTP
   ↓
FastAPI
   ↓
Validation / Business Logic
   ↓
SQL
   ↓
Database
   ↓
Persistent State
```

This is much closer to a real backend architecture.

---

## 95. Important Lesson About Storage Abstraction

The biggest architecture lesson is:

```text
API contract
     ≠
storage implementation
```

The application can theoretically evolve:

```text
Python list
     ↓
SQLite
     ↓
PostgreSQL
     ↓
distributed database
```

while keeping:

```text
GET /tasks
POST /tasks
PUT /tasks/{id}
DELETE /tasks/{id}
```

the same for clients.

That separation is a foundational backend engineering principle.

---

## 96. How to Rebuild BE-02 From Scratch

### Step 1

Start from a working FastAPI CRUD API.

### Step 2

Import:

```python
import sqlite3
```

### Step 3

Define:

```python
DATABASE_NAME = "tasks.db"
```

### Step 4

Create a connection helper.

### Step 5

Create the `tasks` table automatically.

### Step 6

Seed three tasks only when the table is empty.

### Step 7

Replace:

```text
GET all
```

with:

```sql
SELECT * FROM tasks;
```

### Step 8

Replace:

```text
GET one
```

with:

```sql
SELECT * FROM tasks WHERE id = ?;
```

### Step 9

Replace POST list append with:

```sql
INSERT INTO tasks ...
```

### Step 10

Use:

```python
cursor.lastrowid
```

for the database-generated ID.

### Step 11

Replace PUT mutation with:

```sql
UPDATE tasks ...
```

### Step 12

Replace DELETE list removal with:

```sql
DELETE FROM tasks ...
```

### Step 13

Remove the old Python task list.

### Step 14

Test persistence across server restart.

### Step 15

Open `tasks.db` in DB Browser.

### Step 16

Run SQL manually.

### Step 17

Update README.

### Step 18

Add database screenshot.

### Step 19

Commit every stage.

### Step 20

Push to GitHub.

---

## 97. BE-02 Debugging Decision Tree

When the database-backed API fails:

### Server?

```text
Is Uvicorn running?
```

### Route?

```text
Does METHOD + PATH exist?
```

### Request?

```text
Is JSON valid?
```

### Validation?

```text
Does title/done satisfy API rules?
```

### Database?

```text
Does tasks.db exist?
```

### Table?

```sql
SELECT * FROM tasks;
```

### Resource?

```sql
SELECT * FROM tasks WHERE id = ?;
```

### Write?

After INSERT/UPDATE/DELETE:

```text
GET the resource again
```

### Persistence?

```text
restart server
GET again
```

This checks each layer systematically.

---

## 98. Quick Revision Quiz

### Database Basics

1. What is persistence?
2. Why did BE-01 lose tasks after restart?
3. Why does BE-02 keep tasks?
4. What exactly is `tasks.db`?
5. What is a table?
6. What is a row?
7. What is a column?
8. What is a primary key?
9. What is a schema?

### SQLite

10. Why does SQLite require no separate server?
11. What happens if `sqlite3.connect("tasks.db")` is called and the file does not exist?
12. Why use `CREATE TABLE IF NOT EXISTS`?
13. Why count rows before inserting seeds?
14. Why is `tasks.db` git-ignored?

### SQL

15. What does `SELECT` do?
16. What does `INSERT` do?
17. What does `UPDATE` do?
18. What does `DELETE` do?
19. What does `WHERE` do?
20. Why can forgetting `WHERE` be dangerous?
21. What does `COUNT(*)` do?

### Python + SQLite

22. What is a database connection?
23. Why use `sqlite3.Row`?
24. What is the difference between `fetchone()` and `fetchall()`?
25. What does `cursor.lastrowid` return?
26. Why does `(task_id,)` contain a comma?
27. What does `bool(row["done"])` do?

### Security

28. What is a parameterized query?
29. What does `?` represent?
30. Why should user data not be directly inserted into SQL strings?

### Architecture

31. What changed between BE-01 and BE-02?
32. What stayed the same?
33. Why can the client not tell whether tasks are stored in memory or SQLite?
34. What is the difference between the API layer and data layer?
35. Why is this separation useful?

### Persistence

36. How did you prove that persistence worked?
37. What happened to `Buy milk` after restarting Uvicorn?
38. Why did task ID 4 get reused during testing?
39. Why should code trust `lastrowid` rather than guessing the next ID?

If I can answer these comfortably, I understand the database migration rather than just remembering the code.

---

## 99. Core Lessons to Remember

1. A database gives the application persistent storage.
2. SQLite stores an entire database in a file.
3. `tasks.db` is the actual database.
4. Tables contain rows and columns.
5. A primary key uniquely identifies a row.
6. SQL is used to interact with relational databases.
7. `SELECT` reads.
8. `INSERT` creates.
9. `UPDATE` modifies.
10. `DELETE` removes.
11. `WHERE` determines which rows are affected.
12. Parameterized queries keep SQL and data separate.
13. `fetchall()` retrieves many rows.
14. `fetchone()` retrieves one row.
15. `lastrowid` gives the ID generated by SQLite.
16. The database should generate task IDs instead of Python guessing them.
17. API validation still matters even when database constraints exist.
18. SQLite can represent booleans using `0` and `1`.
19. Database rows may need conversion before being returned as API JSON.
20. Seed data must not multiply on normal restarts.
21. `CREATE TABLE IF NOT EXISTS` makes startup initialization repeatable.
22. A database can be modified outside the API and the API immediately sees the same data.
23. Persistence is proven by restarting the application and verifying the data remains.
24. The API contract can stay the same while the storage implementation changes.
25. The API layer and data layer are separate concerns.
26. A staged migration is easier to test and debug than a full rewrite.
27. Git commits should represent meaningful working checkpoints.
28. Generated local databases usually should not be committed.
29. Clean project setup should create the database automatically.
30. Moving from memory to SQLite is the first major step from a demo backend toward a persistent backend.

---

## 100. One-Sentence Memory Hook

> A backend API receives HTTP requests, validates them, translates application operations into SQL queries, stores persistent state in a database, and returns the same API contract regardless of how that data is stored.

---

## 101. Shortest Possible BE-02 Summary

```text
BE-01:
FastAPI → Python list → RAM

BE-02:
FastAPI → SQL → SQLite → tasks.db
```

And:

```text
POST   → INSERT
GET    → SELECT
PUT    → UPDATE
DELETE → DELETE
```

The endpoints stayed the same.

The storage became persistent.

