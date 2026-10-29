import streamlit as st
from auth import require_login, logout_button

# Check authentication on every page
require_login()
logout_button()


import sqlite3

import pandas as pd
import streamlit as st

from database import get_connection

st.set_page_config(
    page_title="Course Management | StudentHub Pro",
    page_icon="📚",
    layout="wide"
)

st.title("📚 Course Management")
st.write("Add and manage academic courses.")

st.divider()

# -----------------------------------
# ADD COURSE
# -----------------------------------

st.subheader("➕ Add New Course")

with st.form("add_course_form", clear_on_submit=True):

    col1, col2 = st.columns(2)

    with col1:
        course_code = st.text_input(
            "Course Code *",
            placeholder="e.g. CS101"
        )

        course_name = st.text_input(
            "Course Name *",
            placeholder="e.g. Python Programming"
        )

    with col2:
        department = st.selectbox(
            "Department",
            [
                "CSE",
                "IT",
                "ECE",
                "EEE",
                "Mechanical",
                "Civil",
                "Other"
            ]
        )

        credits = st.selectbox(
            "Course Credits",
            [1, 2, 3, 4, 5, 6]
        )

    submitted = st.form_submit_button(
        "Add Course",
        type="primary",
        use_container_width=True
    )

    if submitted:

        if not course_code.strip() or not course_name.strip():
            st.error("Course code and name are required.")

        else:
            try:
                with get_connection() as conn:

                    conn.execute(
                        """
                        INSERT INTO courses
                        (course_code, course_name, department, credits)
                        VALUES (?, ?, ?, ?)
                        """,
                        (
                            course_code.strip().upper(),
                            course_name.strip(),
                            department,
                            credits
                        )
                    )

                st.success("Course added successfully!")
                st.rerun()

            except sqlite3.IntegrityError:
                st.error(
                    "This course code already exists. "
                    "Please use a unique course code."
                )


st.divider()

# -----------------------------------
# VIEW COURSES
# -----------------------------------

st.subheader("📋 Available Courses")

with get_connection() as conn:
    courses = pd.read_sql_query(
        """
        SELECT
            id,
            course_code,
            course_name,
            department,
            credits
        FROM courses
        ORDER BY course_code
        """,
        conn
    )

if courses.empty:

    st.info("No courses have been added yet.")

else:

    st.dataframe(
        courses.drop(columns=["id"]),
        use_container_width=True,
        hide_index=True
    )

    st.caption(f"Total courses: {len(courses)}")

    st.download_button(
        "⬇️ Download Courses CSV",
        data=courses.drop(columns=["id"]).to_csv(index=False),
        file_name="studenthub_courses.csv",
        mime="text/csv"
    )

    st.divider()

    # -----------------------------------
    # DELETE COURSE
    # -----------------------------------

    st.subheader("🗑️ Delete Course")

    course_options = {
        f"{row.course_code} — {row.course_name}": row.id
        for row in courses.itertuples()
    }

    selected_course = st.selectbox(
        "Select a course",
        list(course_options.keys())
    )

    confirm = st.checkbox(
        "I confirm that I want to delete this course."
    )

    if st.button(
        "Delete Course",
        disabled=not confirm
    ):

        with get_connection() as conn:
            conn.execute(
                "DELETE FROM courses WHERE id = ?",
                (course_options[selected_course],)
            )

        st.success("Course deleted successfully!")
        st.rerun()

from auth import require_login, logout_button

require_login()
logout_button()
