from __future__ import annotations
import psycopg

PGHOST = "127.0.0.1"
PGPORT = 5432
PGUSER = "postgres"
PGPASSWORD = "Pupsik99!"
DB_NAME = "task_manager"

def get_conn():
    return psycopg.connect(
        host=PGHOST, port=PGPORT, user=PGUSER, password=PGPASSWORD, dbname=DB_NAME
    )

def q1_tasks_by_user(user_id: int):
    sql = "SELECT * FROM tasks WHERE user_id = %s ORDER BY id;"
    return sql, (user_id,)

def q2_tasks_by_status_name(name: str):
    sql = """
    SELECT * FROM tasks
    WHERE status_id = (SELECT id FROM status WHERE name = %s)
    ORDER BY id;
    """
    return sql, (name,)

def q3_update_task_status(task_id: int, status_name: str):
    sql = """
    UPDATE tasks
       SET status_id = (SELECT id FROM status WHERE name = %s)
     WHERE id = %s;
    """
    return sql, (status_name, task_id)

def q4_users_without_tasks():
    sql = """
    SELECT u.*
      FROM users u
     WHERE u.id NOT IN (SELECT DISTINCT user_id FROM tasks)
     ORDER BY u.id;
    """
    return sql, ()

def q5_insert_task_for_user(user_id: int, title: str, description: str | None, status_name: str = "new"):
    sql = """
    INSERT INTO tasks (title, description, status_id, user_id)
    VALUES (%s, %s,
           (SELECT id FROM status WHERE name = %s),
           %s)
    RETURNING id;
    """
    return sql, (title, description, status_name, user_id)

def q6_not_completed_tasks():
    sql = """
    SELECT t.*
      FROM tasks t
      JOIN status s ON s.id = t.status_id
     WHERE s.name <> 'completed'
     ORDER BY t.id;
    """
    return sql, ()

def q7_delete_task(task_id: int):
    sql = "DELETE FROM tasks WHERE id = %s;"
    return sql, (task_id,)

def q8_find_users_by_email_like(pattern: str):
    sql = "SELECT * FROM users WHERE email LIKE %s ORDER BY id;"
    return sql, (pattern,)

def q9_update_user_name(user_id: int, new_name: str):
    sql = "UPDATE users SET fullname = %s WHERE id = %s;"
    return sql, (new_name, user_id)

def q10_tasks_count_by_status():
    sql = """
    SELECT s.name AS status, COUNT(t.id) AS task_count
      FROM status s
 LEFT JOIN tasks t ON t.status_id = s.id
  GROUP BY s.name
  ORDER BY task_count DESC, s.name;
    """
    return sql, ()

def q11_tasks_for_users_with_email_domain(domain_pattern: str):
    sql = """
    SELECT t.*
      FROM tasks t
      JOIN users u ON u.id = t.user_id
     WHERE u.email LIKE %s
     ORDER BY t.id;
    """
    return sql, (domain_pattern,)

def q12_tasks_without_description():
    sql = "SELECT * FROM tasks WHERE description IS NULL OR description = '' ORDER BY id;"
    return sql, ()

def q13_users_with_in_progress_tasks():
    sql = """
    SELECT u.fullname, t.title, t.id
      FROM users u
      JOIN tasks t  ON t.user_id = u.id
      JOIN status s ON s.id = t.status_id
     WHERE s.name = 'in progress'
     ORDER BY u.fullname, t.id;
    """
    return sql, ()

def q14_users_and_task_counts():
    sql = """
    SELECT u.id, u.fullname, COUNT(t.id) AS tasks_count
      FROM users u
 LEFT JOIN tasks t ON t.user_id = u.id
  GROUP BY u.id, u.fullname
  ORDER BY tasks_count DESC, u.fullname;
    """
    return sql, ()

ACTIONS = {
    "1": ("Усі завдання користувача (за user_id)", q1_tasks_by_user, True),
    "2": ("Завдання за статусом (name)", q2_tasks_by_status_name, True),
    "3": ("Оновити статус завдання", q3_update_task_status, True),
    "4": ("Користувачі без жодного завдання", q4_users_without_tasks, False),
    "5": ("Додати нове завдання для користувача", q5_insert_task_for_user, True),
    "6": ("Незавершені завдання", q6_not_completed_tasks, False),
    "7": ("Видалити завдання за id", q7_delete_task, True),
    "8": ("Користувачі за email LIKE", q8_find_users_by_email_like, True),
    "9": ("Оновити ім'я користувача", q9_update_user_name, True),
    "10": ("К-сть завдань за статусами", q10_tasks_count_by_status, False),
    "11": ("Завдання для email-домену", q11_tasks_for_users_with_email_domain, True),
    "12": ("Завдання без опису", q12_tasks_without_description, False),
    "13": ("Користувачі та їхні завдання у 'in progress'", q13_users_with_in_progress_tasks, False),
    "14": ("Користувачі та к-сть їх завдань", q14_users_and_task_counts, False),
}

def main():
    print("\n=== Task Manager — SQL queries ===")
    for k, (title, _, need_args) in ACTIONS.items():
        print(f"{k}) {title}{' *args' if need_args else ''}")
    choice = input("Обери номер (або 0 для виходу): ").strip()
    if choice == "0" or choice not in ACTIONS:
        return

    title, builder, need_args = ACTIONS[choice]
    args = ()
    if builder is q1_tasks_by_user:
        args = (int(input("user_id: ").strip()),)
    elif builder is q2_tasks_by_status_name:
        args = (input("status name (new/in progress/completed): ").strip(),)
    elif builder is q3_update_task_status:
        args = (int(input("task_id: ").strip()), input("new status: ").strip())
    elif builder is q5_insert_task_for_user:
        uid = int(input("user_id: ").strip())
        title_ = input("title: ").strip()
        desc = input("description (optional, Enter=empty): ").strip() or None
        st = input("status (default 'new'): ").strip() or "new"
        args = (uid, title_, desc, st)
    elif builder is q7_delete_task:
        args = (int(input("task_id: ").strip()),)
    elif builder is q8_find_users_by_email_like:
        args = (input("pattern (e.g. %@gmail.com): ").strip(),)
    elif builder is q9_update_user_name:
        args = (int(input("user_id: ").strip()), input("new fullname: ").strip())
    elif builder is q11_tasks_for_users_with_email_domain:
        args = (input("domain pattern (e.g. %@example.com): ").strip(),)

    sql, params = builder(*args) if need_args else builder()

    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(sql, params)
            if sql.strip().upper().startswith("SELECT"):
                rows = cur.fetchall()
                print("\n--- RESULT ---")
                for r in rows:
                    print(r)
            else:
                conn.commit()
                print("✅ Done.")

if __name__ == "__main__":
    main()
