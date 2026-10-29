
import streamlit as st
from auth import require_login, logout_button

# Check authentication on every page
require_login()
logout_button()
import sqlite3

import pandas as pd
import streamlit as st

from database import get_connection, get_all_students

st.set_page_config(
    page_title="Marks Management | StudentHub Pro",
    page_icon="📝",
    layout="wide"
)

st.title("📝 Marks Management")
st.write(
    "Record student marks and automatically calculate grades."
)

st.divider()

students = get_all_students()

if not students:
    st.warning(
        "No students found. Register students before entering marks."
    )
    st.stop()


# -----------------------------------
# ADD OR UPDATE MARKS
# -----------------------------------

st.subheader("➕ Enter Student Marks")

student_options = {
    f"{s['roll_number']} — {s['name']}": s["id"]
    for s in students
}

with st.form("marks_form"):

    selected_student = st.selectbox(
        "Select Student",
        list(student_options.keys())
    )

    subject = st.text_input(
        "Subject Name",
        placeholder="e.g. Python Programming"
    )

    marks = st.number_input(
        "Marks (0–100)",
        min_value=0.0,
        max_value=100.0,
        value=0.0,
        step=1.0
    )

    submitted = st.form_submit_button(
        "Save Marks",
        type="primary",
        use_container_width=True
    )

    if submitted:

        if not subject.strip():
            st.error("Please enter a subject name.")

        else:
            try:
                with get_connection() as conn:

                    conn.execute(
                        """
                        INSERT INTO marks
                        (student_id, subject, marks)
                        VALUES (?, ?, ?)
                        ON CONFLICT(student_id, subject)
                        DO UPDATE SET marks = excluded.marks
                        """,
                        (
                            student_options[selected_student],
                            subject.strip(),
                            marks
                        )
                    )

                st.success(
                    "Marks saved successfully! "
                    "Existing marks for this student and subject "
                    "will be updated."
                )

                st.rerun()

            except sqlite3.Error as error:
                st.error(f"Database error: {error}")


st.divider()


# -----------------------------------
# VIEW MARKS
# -----------------------------------

st.subheader("📋 Student Academic Records")

with get_connection() as conn:

    marks_df = pd.read_sql_query(
        """
        SELECT
            s.roll_number AS 'Roll Number',
            s.name AS 'Student Name',
            s.department AS 'Department',
            m.subject AS 'Subject',
            m.marks AS 'Marks'
        FROM marks m
        JOIN students s
            ON s.id = m.student_id
        ORDER BY s.roll_number, m.subject
        """,
        conn
    )

if marks_df.empty:

    st.info("No marks have been entered yet.")

else:

    marks_df["Result"] = marks_df["Marks"].apply(
        lambda value: "Pass" if value >= 40 else "Fail"
    )

    marks_df["Grade"] = marks_df["Marks"].apply(
        lambda value:
            "A+" if value >= 90 else
            "A" if value >= 80 else
            "B" if value >= 70 else
            "C" if value >= 60 else
            "D" if value >= 40 else
            "F"
    )

    st.dataframe(
        marks_df,
        use_container_width=True,
        hide_index=True
    )

    st.download_button(
        "⬇️ Download Marks CSV",
        data=marks_df.to_csv(index=False),
        file_name="studenthub_marks.csv",
        mime="text/csv"
    )


st.divider()


# -----------------------------------
# STUDENT PERFORMANCE SUMMARY
# -----------------------------------

st.subheader("🏆 Student Performance Summary")

with get_connection() as conn:

    summary = pd.read_sql_query(
        """
        SELECT
            s.roll_number AS 'Roll Number',
            s.name AS 'Student Name',
            s.department AS 'Department',
            COUNT(m.id) AS 'Subjects',
            ROUND(AVG(m.marks), 2) AS 'Average Marks',
            SUM(CASE WHEN m.marks < 40 THEN 1 ELSE 0 END)
                AS 'Failed Subjects'
        FROM students s
        JOIN marks m
            ON s.id = m.student_id
        GROUP BY s.id
        ORDER BY AVG(m.marks) DESC
        """,
        conn
    )

if summary.empty:

    st.info(
        "Performance summaries will appear after marks are entered."
    )

else:

    summary["Overall Grade"] = summary["Average Marks"].apply(
        lambda value:
            "A+" if value >= 90 else
            "A" if value >= 80 else
            "B" if value >= 70 else
            "C" if value >= 60 else
            "D" if value >= 40 else
            "F"
    )

    st.dataframe(
        summary,
        use_container_width=True,
        hide_index=True
    )

    st.subheader("🥇 Top Performers")

    top_students = summary.head(5)

    st.dataframe(
        top_students,
        use_container_width=True,
        hide_index=True
    )

from auth import require_login, logout_button

require_login()
logout_button()
