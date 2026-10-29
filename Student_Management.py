import re

import pandas as pd
import streamlit as st

from database import (
    add_student,
    delete_student,
    get_all_students,
    search_students,
    update_student
)

st.set_page_config(
    page_title="Student Management | StudentHub Pro",
    page_icon="👨‍🎓",
    layout="wide"
)

st.title("👨‍🎓 Student Management")
st.write(
    "Register, search, update, and manage student records."
)

st.divider()

departments = [
    "CSE",
    "IT",
    "ECE",
    "EEE",
    "Mechanical",
    "Civil",
    "Other"
]


def valid_email(email):
    if not email:
        return True

    return bool(
        re.fullmatch(
            r"[^@\s]+@[^@\s]+\.[^@\s]+",
            email
        )
    )


# -----------------------------------
# REGISTER STUDENT
# -----------------------------------

st.subheader("➕ Register a New Student")

with st.form("add_student_form", clear_on_submit=True):

    col1, col2 = st.columns(2)

    with col1:
        roll_number = st.text_input(
            "Roll Number *",
            placeholder="e.g. 23CS001"
        )

        name = st.text_input(
            "Full Name *",
            placeholder="Enter student name"
        )

        email = st.text_input(
            "Email Address",
            placeholder="student@example.com"
        )

    with col2:
        department = st.selectbox(
            "Department *",
            departments
        )

        year = st.selectbox(
            "Year of Study *",
            [1, 2, 3, 4]
        )

    submitted = st.form_submit_button(
        "Register Student",
        type="primary",
        use_container_width=True
    )

    if submitted:

        if not roll_number.strip() or not name.strip():
            st.error(
                "Please enter both the roll number and name."
            )

        elif not valid_email(email.strip()):
            st.error("Please enter a valid email address.")

        else:
            try:
                add_student(
                    roll_number,
                    name,
                    email,
                    department,
                    year
                )

                st.success(
                    f"Student {name.strip()} registered successfully!"
                )

                st.rerun()

            except Exception as error:
                if "UNIQUE constraint failed" in str(error):
                    st.error(
                        "This roll number already exists. "
                        "Please enter a unique roll number."
                    )
                else:
                    st.error(
                        f"Unable to register student: {error}"
                    )


st.divider()


# -----------------------------------
# SEARCH AND VIEW STUDENTS
# -----------------------------------

st.subheader("📋 Student Records")

keyword = st.text_input(
    "🔍 Search students",
    placeholder="Search by name, roll number, or department"
)

if keyword.strip():
    records = search_students(keyword)
else:
    records = get_all_students()

if records:

    df = pd.DataFrame(records)

    display_columns = [
        "roll_number",
        "name",
        "email",
        "department",
        "year"
    ]

    st.dataframe(
        df[display_columns],
        use_container_width=True,
        hide_index=True
    )

    st.caption(f"Showing {len(records)} student record(s).")

else:
    st.info(
        "No student records found. Register your first student above."
    )


st.divider()


# -----------------------------------
# UPDATE STUDENT
# -----------------------------------

st.subheader("✏️ Update Student Details")

all_students = get_all_students()

if all_students:

    student_options = {
        f"{s['roll_number']} — {s['name']}": s
        for s in all_students
    }

    selected_label = st.selectbox(
        "Select a student to update",
        list(student_options.keys()),
        key="update_student"
    )

    selected = student_options[selected_label]

    with st.form("update_student_form"):

        col1, col2 = st.columns(2)

        with col1:
            new_roll = st.text_input(
                "Roll Number",
                value=selected["roll_number"]
            )

            new_name = st.text_input(
                "Full Name",
                value=selected["name"]
            )

            new_email = st.text_input(
                "Email Address",
                value=selected["email"] or ""
            )

        with col2:
            current_department = (
                selected["department"]
                if selected["department"] in departments
                else "Other"
            )

            new_department = st.selectbox(
                "Department",
                departments,
                index=departments.index(current_department)
            )

            new_year = st.selectbox(
                "Year of Study",
                [1, 2, 3, 4],
                index=[1, 2, 3, 4].index(selected["year"])
            )

        update_clicked = st.form_submit_button(
            "Save Changes",
            type="primary"
        )

        if update_clicked:

            if not new_roll.strip() or not new_name.strip():
                st.error("Roll number and name are required.")

            elif not valid_email(new_email.strip()):
                st.error("Please enter a valid email address.")

            else:
                try:
                    update_student(
                        selected["id"],
                        new_roll,
                        new_name,
                        new_email,
                        new_department,
                        new_year
                    )

                    st.success("Student details updated successfully!")

                    st.rerun()

                except Exception as error:
                    if "UNIQUE constraint failed" in str(error):
                        st.error("That roll number is already in use.")
                    else:
                        st.error(f"Update failed: {error}")

else:
    st.info("Register a student before using this feature.")


st.divider()


# -----------------------------------
# DELETE STUDENT
# -----------------------------------

st.subheader("🗑️ Delete Student")

if all_students:

    delete_options = {
        f"{s['roll_number']} — {s['name']}": s["id"]
        for s in all_students
    }

    delete_label = st.selectbox(
        "Select a student to delete",
        list(delete_options.keys()),
        key="delete_student"
    )

    confirm_delete = st.checkbox(
        "I confirm that I want to permanently delete this student."
    )

    if st.button(
        "Delete Selected Student",
        type="secondary",
        disabled=not confirm_delete
    ):

        delete_student(delete_options[delete_label])

        st.success("Student record deleted successfully!")

        st.rerun()

else:
    st.info("There are no student records to delete.")
from auth import require_login, logout_button

require_login()
logout_button()