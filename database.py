import sqlite3

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

# Execute schema check
ensure_extended_schema()

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
