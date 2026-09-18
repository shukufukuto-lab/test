import sqlite3
from datetime import datetime
from pathlib import Path

DB_PATH = Path(__file__).parent / "fellow.db"


def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_conn()
    cur = conn.cursor()
    cur.executescript(
        """
        CREATE TABLE IF NOT EXISTS projects (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            start_date TEXT,
            end_date TEXT,
            keywords TEXT,
            status TEXT DEFAULT '進行中'
        );

        CREATE TABLE IF NOT EXISTS staff (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            monthly_capacity_hours REAL DEFAULT 160
        );

        CREATE TABLE IF NOT EXISTS plans (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            project_id INTEGER NOT NULL,
            staff_id INTEGER NOT NULL,
            month TEXT NOT NULL,
            planned_hours REAL DEFAULT 0,
            UNIQUE(project_id, staff_id, month),
            FOREIGN KEY(project_id) REFERENCES projects(id),
            FOREIGN KEY(staff_id) REFERENCES staff(id)
        );

        CREATE TABLE IF NOT EXISTS time_entries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            project_id INTEGER NOT NULL,
            staff_id INTEGER NOT NULL,
            start_time TEXT NOT NULL,
            end_time TEXT NOT NULL,
            source TEXT DEFAULT 'manual',
            memo TEXT,
            FOREIGN KEY(project_id) REFERENCES projects(id),
            FOREIGN KEY(staff_id) REFERENCES staff(id)
        );
        """
    )
    conn.commit()

    cur.execute("SELECT COUNT(*) FROM staff")
    if cur.fetchone()[0] == 0:
        cur.executemany(
            "INSERT INTO staff (name, monthly_capacity_hours) VALUES (?, ?)",
            [("田中", 160), ("佐藤", 160), ("鈴木", 140)],
        )
        cur.execute(
            "INSERT INTO projects (name, start_date, end_date, keywords, status) VALUES (?, ?, ?, ?, ?)",
            ("A案件", "2026-09-01", "2026-09-30", "projectA,PJ-A", "進行中"),
        )
        cur.execute(
            "INSERT INTO projects (name, start_date, end_date, keywords, status) VALUES (?, ?, ?, ?, ?)",
            ("B案件", "2026-09-15", "2026-10-10", "projectB", "進行中"),
        )
        conn.commit()
    conn.close()


# --- Projects ---
def list_projects():
    conn = get_conn()
    rows = conn.execute("SELECT * FROM projects ORDER BY id").fetchall()
    conn.close()
    return rows


def add_project(name, start_date, end_date, keywords, status="進行中"):
    conn = get_conn()
    conn.execute(
        "INSERT INTO projects (name, start_date, end_date, keywords, status) VALUES (?, ?, ?, ?, ?)",
        (name, start_date, end_date, keywords, status),
    )
    conn.commit()
    conn.close()


def update_project(pid, name, start_date, end_date, keywords, status):
    conn = get_conn()
    conn.execute(
        "UPDATE projects SET name=?, start_date=?, end_date=?, keywords=?, status=? WHERE id=?",
        (name, start_date, end_date, keywords, status, pid),
    )
    conn.commit()
    conn.close()


def delete_project(pid):
    conn = get_conn()
    conn.execute("DELETE FROM projects WHERE id=?", (pid,))
    conn.commit()
    conn.close()


# --- Staff ---
def list_staff():
    conn = get_conn()
    rows = conn.execute("SELECT * FROM staff ORDER BY id").fetchall()
    conn.close()
    return rows


def add_staff(name, capacity):
    conn = get_conn()
    conn.execute(
        "INSERT INTO staff (name, monthly_capacity_hours) VALUES (?, ?)",
        (name, capacity),
    )
    conn.commit()
    conn.close()


def update_staff(sid, name, capacity):
    conn = get_conn()
    conn.execute(
        "UPDATE staff SET name=?, monthly_capacity_hours=? WHERE id=?",
        (name, capacity, sid),
    )
    conn.commit()
    conn.close()


def delete_staff(sid):
    conn = get_conn()
    conn.execute("DELETE FROM staff WHERE id=?", (sid,))
    conn.commit()
    conn.close()


# --- Plans ---
def get_plan(project_id, staff_id, month):
    conn = get_conn()
    row = conn.execute(
        "SELECT * FROM plans WHERE project_id=? AND staff_id=? AND month=?",
        (project_id, staff_id, month),
    ).fetchone()
    conn.close()
    return row


def set_plan(project_id, staff_id, month, hours):
    conn = get_conn()
    conn.execute(
        """
        INSERT INTO plans (project_id, staff_id, month, planned_hours)
        VALUES (?, ?, ?, ?)
        ON CONFLICT(project_id, staff_id, month)
        DO UPDATE SET planned_hours=excluded.planned_hours
        """,
        (project_id, staff_id, month, hours),
    )
    conn.commit()
    conn.close()


def list_plans_for_month(month):
    conn = get_conn()
    rows = conn.execute("SELECT * FROM plans WHERE month=?", (month,)).fetchall()
    conn.close()
    return rows


# --- Time entries ---
def add_time_entry(project_id, staff_id, start_time, end_time, source="manual", memo=""):
    conn = get_conn()
    conn.execute(
        """
        INSERT INTO time_entries (project_id, staff_id, start_time, end_time, source, memo)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (project_id, staff_id, start_time, end_time, source, memo),
    )
    conn.commit()
    conn.close()


def delete_time_entry(eid):
    conn = get_conn()
    conn.execute("DELETE FROM time_entries WHERE id=?", (eid,))
    conn.commit()
    conn.close()


def list_time_entries_for_date(staff_id, date_str):
    conn = get_conn()
    rows = conn.execute(
        """
        SELECT te.*, p.name as project_name FROM time_entries te
        JOIN projects p ON p.id = te.project_id
        WHERE te.staff_id=? AND date(te.start_time)=?
        ORDER BY te.start_time
        """,
        (staff_id, date_str),
    ).fetchall()
    conn.close()
    return rows


def sum_actual_hours_for_month(month):
    conn = get_conn()
    rows = conn.execute(
        """
        SELECT project_id, staff_id,
               SUM((julianday(end_time) - julianday(start_time)) * 24) as actual_hours
        FROM time_entries
        WHERE strftime('%Y-%m', start_time) = ?
        GROUP BY project_id, staff_id
        """,
        (month,),
    ).fetchall()
    conn.close()
    return rows
