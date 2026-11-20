from .database import get_connection

class TaskRepository:
    def all(self, search=""):
        with get_connection() as conn:
            if search.strip():
                q = f"%{search.strip()}%"
                rows = conn.execute(
                    "SELECT * FROM tasks WHERE title LIKE ? OR description LIKE ? ORDER BY "
                    "CASE status WHEN 'In Progress' THEN 0 WHEN 'Not Started' THEN 1 ELSE 2 END, "
                    "due_date IS NULL, due_date, due_time",
                    (q, q)
                ).fetchall()
            else:
                rows = conn.execute(
                    "SELECT * FROM tasks ORDER BY "
                    "CASE status WHEN 'In Progress' THEN 0 WHEN 'Not Started' THEN 1 ELSE 2 END, "
                    "due_date IS NULL, due_date, due_time"
                ).fetchall()
            return [dict(r) for r in rows]

    def create(self, title, description, due_date, due_time, priority):
        with get_connection() as conn:
            conn.execute(
                "INSERT INTO tasks(title, description, due_date, due_time, priority) VALUES(?,?,?,?,?)",
                (title, description, due_date, due_time, priority)
            )

    def update_status(self, task_id, status):
        with get_connection() as conn:
            conn.execute("UPDATE tasks SET status=? WHERE id=?", (status, task_id))

    def delete(self, task_id):
        with get_connection() as conn:
            conn.execute("DELETE FROM tasks WHERE id=?", (task_id,))

    def counts(self):
        with get_connection() as conn:
            total = conn.execute("SELECT COUNT(*) FROM tasks").fetchone()[0]
            done = conn.execute("SELECT COUNT(*) FROM tasks WHERE status='Completed'").fetchone()[0]
            active = conn.execute("SELECT COUNT(*) FROM tasks WHERE status!='Completed'").fetchone()[0]
            return total, active, done
