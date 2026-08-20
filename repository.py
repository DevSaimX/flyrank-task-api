import os

import psycopg
from dotenv import load_dotenv
from psycopg.rows import dict_row


load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise RuntimeError(
        "DATABASE_URL is not configured. "
        "Create a .env file based on .env.example."
    )


def get_connection():
    return psycopg.connect(
        DATABASE_URL,
        row_factory=dict_row,
    )


def initialize_database():
    with get_connection() as connection:
        with connection.cursor() as cursor:

            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS tasks (
                    id SERIAL PRIMARY KEY,
                    title TEXT NOT NULL,
                    done BOOLEAN NOT NULL DEFAULT FALSE
                )
                """
            )

            cursor.execute(
                "SELECT COUNT(*) AS count FROM tasks"
            )

            row = cursor.fetchone()

            if row is None:
                raise RuntimeError(
                    "Failed to count tasks."
                )

            if row["count"] == 0:
                cursor.executemany(
                    """
                    INSERT INTO tasks (title, done)
                    VALUES (%s, %s)
                    """,
                    [
                        ("Learn FastAPI basics", False),
                        ("Build CRUD API", False),
                        ("Test API endpoints", True),
                    ],
                )


def get_all_tasks():
    with get_connection() as connection:
        with connection.cursor() as cursor:

            cursor.execute(
                """
                SELECT id, title, done
                FROM tasks
                ORDER BY id
                """
            )

            return cursor.fetchall()


def get_task(task_id: int):
    with get_connection() as connection:
        with connection.cursor() as cursor:

            cursor.execute(
                """
                SELECT id, title, done
                FROM tasks
                WHERE id = %s
                """,
                (task_id,),
            )

            return cursor.fetchone()


def create_task(title: str):
    with get_connection() as connection:
        with connection.cursor() as cursor:

            cursor.execute(
                """
                INSERT INTO tasks (title, done)
                VALUES (%s, %s)
                RETURNING id, title, done
                """,
                (title, False),
            )

            return cursor.fetchone()


def update_task(
    task_id: int,
    title: str | None = None,
    done: bool | None = None,
):
    existing = get_task(task_id)

    if existing is None:
        return None

    new_title = (
        title
        if title is not None
        else existing["title"]
    )

    new_done = (
        done
        if done is not None
        else existing["done"]
    )

    with get_connection() as connection:
        with connection.cursor() as cursor:

            cursor.execute(
                """
                UPDATE tasks
                SET title = %s, done = %s
                WHERE id = %s
                RETURNING id, title, done
                """,
                (
                    new_title,
                    new_done,
                    task_id,
                ),
            )

            return cursor.fetchone()


def delete_task(task_id: int):
    with get_connection() as connection:
        with connection.cursor() as cursor:

            cursor.execute(
                """
                DELETE FROM tasks
                WHERE id = %s
                RETURNING id
                """,
                (task_id,),
            )

            return cursor.fetchone() is not None