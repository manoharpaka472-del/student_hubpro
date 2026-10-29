import sqlite3
from pathlib import Path

# Store the database inside the project folder.
DB_PATH = Path(__file__).resolve().parent / "students.db"


def get_connection():
    """Create a connection to the SQLite database."""
    conn = sqlite3.connect(DB_PATH, timeout=10)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db():
    """Create database tables if they don't exist."""

    with get_connection() as conn:

        conn.execute("""
            CREATE TABLE IF NOT EXISTS students (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                roll_number TEXT UNIQUE NOT NULL,
                name TEXT NOT NULL,
                email TEXT,
                department TEXT NOT NULL,
                year INTEGER NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        conn.execute("""
            CREATE TABLE IF NOT EXISTS courses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                course_code TEXT UNIQUE NOT NULL,
                course_name TEXT NOT NULL,
                department TEXT NOT NULL,
                credits INTEGER DEFAULT 3
            )
        """)

        conn.execute("""
            CREATE TABLE IF NOT EXISTS marks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                student_id INTEGER NOT NULL,
                subject TEXT NOT NULL,
                marks REAL NOT NULL CHECK(marks >= 0 AND marks <= 100),
                UNIQUE(student_id, subject),
                FOREIGN KEY(student_id)
                    REFERENCES students(id)
                    ON DELETE CASCADE
            )
        """)


def add_student(roll_number, name, email, department, year):
    """Register a new student."""

    with get_connection() as conn:
        cursor = conn.execute("""
            INSERT INTO students
            (roll_number, name, email, department, year)
            VALUES (?, ?, ?, ?, ?)
        """, (
            roll_number.strip(),
            name.strip(),
            email.strip(),
            department,
            year
        ))

        return cursor.lastrowid


def get_all_students():
    """Return all student records."""

    with get_connection() as conn:
        rows = conn.execute("""
            SELECT *
            FROM students
            ORDER BY id DESC
        """).fetchall()

        return [dict(row) for row in rows]


def search_students(keyword=""):
    """Search students by name, roll number, or department."""

    keyword = keyword.strip()

    with get_connection() as conn:
        rows = conn.execute("""
            SELECT *
            FROM students
            WHERE roll_number LIKE ?
               OR name LIKE ?
               OR department LIKE ?
            ORDER BY name
        """, (
            f"%{keyword}%",
            f"%{keyword}%",
            f"%{keyword}%"
        )).fetchall()

        return [dict(row) for row in rows]


def update_student(
    student_id,
    roll_number,
    name,
    email,
    department,
    year
):
    """Update an existing student."""

    with get_connection() as conn:
        conn.execute("""
            UPDATE students
            SET roll_number = ?,
                name = ?,
                email = ?,
                department = ?,
                year = ?
            WHERE id = ?
        """, (
            roll_number.strip(),
            name.strip(),
            email.strip(),
            department,
            year,
            student_id
        ))


def delete_student(student_id):
    """Delete a student and associated marks."""

    with get_connection() as conn:
        conn.execute(
            "DELETE FROM students WHERE id = ?",
            (student_id,)
        )


def get_dashboard_stats():
    """Calculate dashboard statistics from the database."""

    with get_connection() as conn:

        total_students = conn.execute("""
            SELECT COUNT(*) FROM students
        """).fetchone()[0]

        total_departments = conn.execute("""
            SELECT COUNT(DISTINCT department)
            FROM students
        """).fetchone()[0]

        average_marks = conn.execute("""
            SELECT AVG(marks) FROM marks
        """).fetchone()[0]

        total_marks = conn.execute("""
            SELECT COUNT(*) FROM marks
        """).fetchone()[0]

        passed_marks = conn.execute("""
            SELECT COUNT(*)
            FROM marks
            WHERE marks >= 40
        """).fetchone()[0]

    pass_percentage = (
        passed_marks / total_marks * 100
        if total_marks else 0
    )

    return {
        "total_students": total_students,
        "total_departments": total_departments,
        "average_marks": average_marks or 0,
        "pass_percentage": pass_percentage
    }


# Initialize the database when this module is imported.
init_db()