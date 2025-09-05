from __future__ import annotations
import random
from typing import List, Dict

import psycopg
from faker import Faker

PGHOST = "127.0.0.1"
PGPORT = 5432
PGUSER = "postgres"
PGPASSWORD = "Pupsik99!"
DB_NAME = "task_manager"

STATUSES = ["new", "in progress", "completed"]
USERS_COUNT = 20
TASKS_MIN = 2
TASKS_MAX = 6

def connect():
    return psycopg.connect(
        host=PGHOST, port=PGPORT, user=PGUSER, password=PGPASSWORD, dbname=DB_NAME
    )

def seed_statuses(cur) -> None:
    cur.executemany(
        "INSERT INTO status(name) VALUES (%s) ON CONFLICT (name) DO NOTHING",
        [(s,) for s in STATUSES],
    )

def seed_users(cur, n: int) -> List[int]:
    fake = Faker()
    rows = [(fake.name(), fake.unique.email()) for _ in range(n)]
    cur.executemany(
        "INSERT INTO users(fullname, email) VALUES (%s, %s) "
        "ON CONFLICT (email) DO NOTHING",
        rows,
    )
    cur.execute("SELECT id FROM users")
    return [r[0] for r in cur.fetchall()]

def status_map(cur) -> Dict[str, int]:
    cur.execute("SELECT id, name FROM status")
    return {name: sid for sid, name in cur.fetchall()}

def seed_tasks(cur, user_ids: List[int], smap: Dict[str, int]) -> None:
    fake = Faker()
    bulk = []
    for uid in user_ids:
        k = random.randint(TASKS_MIN, TASKS_MAX)
        for _ in range(k):
            title = fake.sentence(nb_words=5).rstrip(".")
            desc = fake.paragraph(nb_sentences=3)
            st = random.choice(STATUSES)
            bulk.append((title, desc, smap[st], uid))
    if bulk:
        cur.executemany(
            "INSERT INTO tasks(title, description, status_id, user_id) "
            "VALUES (%s, %s, %s, %s)",
            bulk,
        )

def main():
    with connect() as conn:
        with conn.cursor() as cur:
            seed_statuses(cur)
            uids = seed_users(cur, USERS_COUNT)
            smap = status_map(cur)
            seed_tasks(cur, uids, smap)
        conn.commit()
    print("✅ Seed completed.")

if __name__ == "__main__":
    main()
