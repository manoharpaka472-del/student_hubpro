import sqlite3

DATABASE_PATH = "students.db"

# ==========================================
# 1. DATABASE CONNECTION
# ==========================================

def get_connection():
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn


# ==========================================
# 2. SCHEMA INITIALIZATION & MIGRATIONS
# ==========================================

def ensure_extended_schema():
    with get_connection() as conn:
        cursor = conn.cursor()

        # Create students table if not exists
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS students (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                roll_number TEXT UNIQUE NOT NULL,
                email TEXT NOT NULL,
                department TEXT NOT NULL,
                year INTEGER NOT NULL,
                password TEXT DEFAULT 'student123'
            )
        """)

        # Add password column to existing students table if missing
        try:
            cursor.execute("ALTER TABLE students ADD COLUMN password TEXT DEFAULT 'student123'")
            conn.commit()
        except sqlite3.OperationalError:
            pass

        # Create courses table if not exists
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS courses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                course_code TEXT UNIQUE NOT NULL,
                course_name TEXT NOT NULL,
                department TEXT NOT NULL,
                credits INTEGER NOT NULL
            )
        """)

        # Create marks table if not exists
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS marks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                student_id INTEGER NOT NULL,
                subject TEXT NOT NULL,
                marks REAL NOT NULL,
                FOREIGN KEY (student_id) REFERENCES students(id)
            )
        """)

        # Create announcements table if not exists
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS announcements (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                message TEXT NOT NULL,
                date_posted TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()

# Run schema setup
ensure_extended_schema()


# ==========================================
# 3. STUDENT MANAGEMENT (CRUD)
# ==========================================

def add_student(name, roll_number, email, department, year, password="student123"):
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO students (name, roll_number, email, department, year, password)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (name, roll_number, email, department, year, password)
        )
        conn.commit()

def get_all_students():
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM students ORDER BY name")
        rows = cursor.fetchall()
        return [dict(row) for row in rows]

def search_students(query):
    with get_connection() as conn:
        cursor = conn.cursor()
        q = f"%{query}%"
        cursor.execute(
            """
            SELECT * FROM students
            WHERE name LIKE ? OR roll_number LIKE ? OR department LIKE ?
            ORDER BY name
            """,
            (q, q, q)
        )
        rows = cursor.fetchall()
        return [dict(row) for row in rows]

def update_student(student_id, name, email, department, year):
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            UPDATE students
            SET name = ?, email = ?, department = ?, year = ?
            WHERE id = ?
            """,
            (name, email, department, year, student_id)
        )
        conn.commit()

def delete_student(student_id):
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM marks WHERE student_id = ?", (student_id,))
        cursor.execute("DELETE FROM students WHERE id = ?", (student_id,))
        conn.commit()

def update_student_password(student_id, new_password):
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE students SET password = ? WHERE id = ?",
            (new_password, student_id)
        )
        conn.commit()


# ==========================================
# 4. DASHBOARD & ANALYTICS METRICS
# ==========================================

def get_dashboard_stats():
    with get_connection() as conn:
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM students")
        total_students = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(DISTINCT department) FROM students")
        total_departments = cursor.fetchone()[0]
        
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


# ==========================================
# 5. CAMPUS ANNOUNCEMENTS
# ==========================================

def add_announcement(title, message):
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO announcements (title, message) VALUES (?, ?)",
            (title, message)
        )
        conn.commit()

def get_announcements():
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT title, message, date_posted FROM announcements ORDER BY id DESC LIMIT 5"
        )
        return cursor.fetchall()
