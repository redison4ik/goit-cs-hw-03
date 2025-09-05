from __future__ import annotations
import psycopg
from psycopg import sql

PGHOST = "127.0.0.1"
PGPORT = 5432
PGUSER = "postgres"
PGPASSWORD = "Pupsik99!"
DB_NAME = "task_manager"

SCHEMA_SQL = """
DROP TABLE IF EXISTS tasks CASCADE;
DROP TABLE IF EXISTS status CASCADE;
DROP TABLE IF EXISTS users CASCADE;

CREATE TABLE users (
    id       SERIAL PRIMARY KEY,
    fullname VARCHAR(100) NOT NULL,
    email    VARCHAR(100) NOT NULL UNIQUE
);

CREATE TABLE status (
    id   SERIAL PRIMARY KEY,
    name VARCHAR(50) NOT NULL UNIQUE
);

CREATE TABLE tasks (
    id          SERIAL PRIMARY KEY,
    title       VARCHAR(100) NOT NULL,
    description TEXT,
    status_id   INTEGER NOT NULL REFERENCES status(id) ON UPDATE CASCADE,
    user_id     INTEGER NOT NULL REFERENCES users(id)  ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_tasks_status_id ON tasks(status_id);
CREATE INDEX IF NOT EXISTS idx_tasks_user_id   ON tasks(user_id);
"""

def create_database_if_absent() -> None:
    conn = psycopg.connect(
        host=PGHOST, port=PGPORT, user=PGUSER, password=PGPASSWORD,
        dbname="postgres", autocommit=True
    )
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT 1 FROM pg_database WHERE datname = %s", (DB_NAME,))
            if cur.fetchone() is None:
                cur.execute(
                    sql.SQL("CREATE DATABASE {} ENCODING 'UTF8'")
                       .format(sql.Identifier(DB_NAME))
                )
                print(f"✅ Database '{DB_NAME}' created.")
            else:
                print(f"ℹ️ Database '{DB_NAME}' already exists.")
    finally:
        conn.close()

def apply_schema() -> None:
    conn = psycopg.connect(
        host=PGHOST, port=PGPORT, user=PGUSER, password=PGPASSWORD, dbname=DB_NAME
    )
    try:
        with conn.cursor() as cur:
            cur.execute(SCHEMA_SQL)
        conn.commit()
        print("✅ Schema applied successfully.")
    finally:
        conn.close()

if __name__ == "__main__":
    create_database_if_absent()
    apply_schema()
