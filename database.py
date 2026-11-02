import sqlite3

DATABASE_PATH = "students.db"

# ==========================================
# 1. DATABASE CONNECTION
# ==========================================

def get_connection():
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


# ==========================================
# 2. SCHEMA INITIALIZATION & MIGRATIONS
# ==========================================

def ensure_extended_schema():
    with get_connection() as conn:
        cursor = conn.cursor()

        # 1. Students Table
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

        # 2. Courses Table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS courses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                course_code TEXT UNIQUE NOT NULL,
                course_name TEXT NOT NULL,
                department TEXT NOT NULL,
                credits INTEGER NOT NULL
            )
        """)

        # 3. Marks Table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS marks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                student_id INTEGER NOT NULL,
                subject TEXT NOT NULL,
                marks REAL NOT NULL,
                FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE
            )
        """)

        # 4. Announcements Table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS announcements (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                message TEXT NOT NULL,
                date_posted TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # 5. Attendance Table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS attendance (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                student_id INTEGER NOT NULL,
                subject TEXT NOT NULL,
                date TEXT NOT NULL,
                status TEXT NOT NULL,
                FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE,
                UNIQUE(student_id, subject, date)
            )
        """)

        # 6. Assignments Table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS assignments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                subject TEXT NOT NULL,
                department TEXT NOT NULL,
                deadline TEXT NOT NULL,
                description TEXT NOT NULL
            )
        """)

        # 7. Assignment Submissions Table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS assignment_submissions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                assignment_id INTEGER NOT NULL,
                student_id INTEGER NOT NULL,
                submission_link TEXT NOT NULL,
                grade TEXT DEFAULT 'Pending Review',
                submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (assignment_id) REFERENCES assignments(id) ON DELETE CASCADE,
                FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE,
                UNIQUE(assignment_id, student_id)
            )
        """)

        # 8. Timetable Table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS timetable (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                department TEXT NOT NULL,
                year INTEGER NOT NULL,
                day_of_week TEXT NOT NULL,
                time_slot TEXT NOT NULL,
                subject TEXT NOT NULL,
                room_no TEXT NOT NULL
            )
        """)

        # 9. Fee Dues Table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS fee_dues (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                student_id INTEGER NOT NULL,
                fee_type TEXT NOT NULL,
                amount REAL NOT NULL,
                due_date TEXT NOT NULL,
                status TEXT DEFAULT 'Unpaid',
                FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE
            )
        """)

        # 10. Feedback Table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS feedback (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                student_id INTEGER NOT NULL,
                subject TEXT NOT NULL,
                rating INTEGER NOT NULL,
                comments TEXT NOT NULL,
                submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE
            )
        """)

        conn.commit()

ensure_extended_schema()


# ==========================================
# 3. STUDENT CRUD OPERATIONS
# ==========================================

def add_student(name, roll_number, email, department, year, password="student123"):
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO students (name, roll_number, email, department, year, password)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (name.strip(), str(roll_number).strip().upper(), email.strip(), department.strip(), int(year), password.strip())
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
        q = f"%{query.strip()}%"
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
            (name.strip(), email.strip(), department.strip(), int(year), student_id)
        )
        conn.commit()

def delete_student(student_id):
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM students WHERE id = ?", (student_id,))
        conn.commit()

def update_student_password(student_id, new_password):
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE students SET password = ? WHERE id = ?",
            (str(new_password).strip(), student_id)
        )
        conn.commit()


# ==========================================
# 4. MARKS CRUD, UPDATE & DELETE
# ==========================================

def update_single_mark(mark_id, new_subject, new_score):
    """Updates an existing mark entry's subject name and score."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE marks SET subject = ?, marks = ? WHERE id = ?",
            (str(new_subject).strip(), float(new_score), int(mark_id))
        )
        conn.commit()

def delete_single_mark(mark_id):
    """Permanently deletes an individual mark record by ID."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM marks WHERE id = ?", (int(mark_id),))
        conn.commit()

def delete_all_marks_for_student(student_id):
    """Permanently removes all marks associated with a student."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM marks WHERE student_id = ?", (int(student_id),))
        conn.commit()


# ==========================================
# 5. DASHBOARD STATISTICS
# ==========================================

def get_dashboard_stats():
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM students")
        total_students = cursor.fetchone()[0] or 0

        cursor.execute("SELECT COUNT(DISTINCT department) FROM students")
        total_departments = cursor.fetchone()[0] or 0

        cursor.execute("SELECT AVG(marks) FROM marks")
        avg_row = cursor.fetchone()[0]
        average_marks = round(avg_row, 2) if avg_row else 0.0

        cursor.execute("SELECT COUNT(*) FROM marks")
        total_marks = cursor.fetchone()[0] or 0

        cursor.execute("SELECT COUNT(*) FROM marks WHERE marks >= 40")
        passed_marks = cursor.fetchone()[0] or 0
        pass_percentage = round((passed_marks / total_marks * 100), 1) if total_marks > 0 else 0.0

        return {
            "total_students": total_students,
            "total_departments": total_departments,
            "average_marks": average_marks,
            "pass_percentage": pass_percentage
        }


# ==========================================
# 6. CAMPUS ANNOUNCEMENTS
# ==========================================

def add_announcement(title, message):
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO announcements (title, message) VALUES (?, ?)",
            (title.strip(), message.strip())
        )
        conn.commit()

def get_announcements():
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT title, message, date_posted FROM announcements ORDER BY id DESC LIMIT 5"
        )
        return cursor.fetchall()


# ==========================================
# 7. ATTENDANCE MANAGEMENT
# ==========================================

def mark_student_attendance(student_id, subject, date_str, status):
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO attendance (student_id, subject, date, status)
            VALUES (?, ?, ?, ?)
            ON CONFLICT(student_id, subject, date) 
            DO UPDATE SET status = excluded.status
            """,
            (student_id, subject.strip(), date_str, status)
        )
        conn.commit()

def get_student_attendance_summary(student_id):
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT 
                subject,
                COUNT(*) as total_classes,
                SUM(CASE WHEN status = 'Present' THEN 1 ELSE 0 END) as attended_classes
            FROM attendance
            WHERE student_id = ?
            GROUP BY subject
            ORDER BY subject
            """,
            (student_id,)
        )
        rows = cursor.fetchall()
        return [dict(row) for row in rows]

def get_student_attendance_records(student_id):
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT date, subject, status
            FROM attendance
            WHERE student_id = ?
            ORDER BY date DESC
            """,
            (student_id,)
        )
        rows = cursor.fetchall()
        return [dict(row) for row in rows]


# ==========================================
# 8. ASSIGNMENTS & SUBMISSIONS
# ==========================================

def add_assignment(title, subject, department, deadline, description):
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO assignments (title, subject, department, deadline, description)
            VALUES (?, ?, ?, ?, ?)
            """,
            (title.strip(), subject.strip(), department.strip(), str(deadline), description.strip())
        )
        conn.commit()

def get_assignments_for_department(department):
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM assignments WHERE department = ? OR department = 'All' ORDER BY id DESC",
            (department,)
        )
        rows = cursor.fetchall()
        return [dict(row) for row in rows]

def submit_assignment(assignment_id, student_id, submission_link):
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO assignment_submissions (assignment_id, student_id, submission_link)
            VALUES (?, ?, ?)
            ON CONFLICT(assignment_id, student_id)
            DO UPDATE SET submission_link = excluded.submission_link, submitted_at = CURRENT
