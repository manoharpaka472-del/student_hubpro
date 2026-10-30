import sqlite3

DATABASE_PATH = "students.db"

# 1. Connection Helper
def get_connection():
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn

# 2. Database Schema Initialization
def ensure_extended_schema():
    with get_connection() as conn:
        cursor = conn.cursor()
        
        # Add password column to students if it doesn't exist
        try:
            cursor.execute("ALTER TABLE students ADD COLUMN password TEXT DEFAULT 'student123'")
            conn.commit()
        except sqlite3.OperationalError:
            pass  # Column already exists

        # Create announcements table if it doesn't exist
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS announcements (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                message TEXT NOT NULL,
                date_posted TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()

# Execute schema update
ensure_extended_schema()

# 3. Core Database Functions
def get_all_students():
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM students ORDER BY name")
        rows = cursor.fetchall()
        return [dict(row) for row in rows]

def get_dashboard_stats():
    with get_connection() as conn:
        cursor = conn.cursor()
        
        # Total students
        cursor.execute("SELECT COUNT(*) FROM students")
        total_students = cursor.fetchone()[0]
        
        # Total departments
        cursor.execute("SELECT COUNT(DISTINCT department) FROM students")
        total_departments = cursor.fetchone()[0]
        
        # Average marks & pass percentage
        cursor.execute("SELECT AVG(marks) FROM marks")
        avg_row = cursor.fetchone()[0]
        average_marks = round(avg_row, 2) if avg_row else 0.0
        
        cursor.execute("SELECT COUNT(*) FROM marks")
        total_marks = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM marks WHERE marks >= 40")
        passed_marks = cursor.fetchone()[0]
        pass_percentage = round((passed_marks / total_marks * 100), 1) if total_marks > 0 else 0.0

        return {
            "total_students": total_students,
            "total_departments": total_departments,
            "average_marks": average_marks,
            "pass_percentage": pass_percentage
        }

# 4. Student Password & Announcement Helpers
def update_student_password(student_id, new_password):
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("UPDATE students SET password = ? WHERE id = ?", (new_password, student_id))
        conn.commit()

def add_announcement(title, message):
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("INSERT INTO announcements (title, message) VALUES (?, ?)", (title, message))
        conn.commit()

def get_announcements():
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT title, message, date_posted FROM announcements ORDER BY id DESC LIMIT 5")
        return cursor.fetchall()
