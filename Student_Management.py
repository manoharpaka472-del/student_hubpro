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

# Header Section
st.title("👨‍🎓 Student Management")
st.markdown("<p style='color: #94a3b8;'>Register, search, update, and manage student records.</p>", unsafe_allow_html=True)
st.divider()

departments = ["Mechanical", "Computer Science", "Electrical", "Civil", "Electronics", "Information Technology"]
academic_years = [1, 2, 3, 4]

# Tabs for management operations
tab_add, tab_view, tab_edit = st.tabs(["➕ Add Student", "📋 Student Directory", "✏️ Edit / Delete"])

# ==========================================
# TAB 1: ADD STUDENT
# ==========================================
with tab_add:
    st.subheader("Register New Student")
    with st.form("add_student_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            name = st.text_input("Full Name *", placeholder="e.g. Rahul Sharma")
            roll_number = st.text_input("Roll Number *", placeholder="e.g. 2505A31020")
            email = st.text_input("Email Address *", placeholder="e.g. rahul@example.com")
        with col2:
            dept = st.selectbox("Department *", departments)
            year = st.selectbox("Academic Year *", academic_years)
            default_pwd = st.text_input("Initial Password", value="student123", type="password")

        submit_btn = st.form_submit_button("Register Student", use_container_width=True)

        if submit_btn:
            if not name.strip() or not roll_number.strip() or not email.strip():
                st.error("Please fill in all required fields marked with *.")
            elif not re.match(r"[^@]+@[^@]+\.[^@]+", email.strip()):
                st.error("Please enter a valid email address.")
            else:
                try:
                    add_student(
                        name=name.strip(),
                        roll_number=roll_number.strip().upper(),
                        email=email.strip(),
                        department=dept,
                        year=int(year),
                        password=default_pwd.strip()
                    )
                    st.success(f"Student **{name.strip()}** ({roll_number.strip().upper()}) registered successfully!")
                except Exception as e:
                    st.error(f"Failed to register student. Roll number might already exist. Error: {e}")

# ==========================================
# TAB 2: VIEW & SEARCH
# ==========================================
with tab_view:
    st.subheader("Student Directory")
    search_query = st.text_input("Search by Name, Roll No, or Department:", "", key="view_search_box")

    if search_query.strip():
        students_list = search_students(search_query.strip())
    else:
        students_list = get_all_students()

    if students_list:
        df_students = pd.DataFrame(students_list)
        cols_to_show = ["roll_number", "name", "email", "department", "year"]
        display_df = df_students[[c for c in cols_to_show if c in df_students.columns]].rename(
            columns={
                "roll_number": "Roll Number",
                "name": "Full Name",
                "email": "Email",
                "department": "Department",
                "year": "Year"
            }
        )
        st.dataframe(display_df, use_container_width=True, hide_index=True)
    else:
        st.info("No matching student records found.")

# ==========================================
# TAB 3: EDIT & DELETE
# ==========================================
with tab_edit:
    st.subheader("Update or Remove Student Record")
    all_current = get_all_students()

    if all_current:
        student_options = {f"{s['roll_number']} - {s['name']}": s for s in all_current}
        selected_label = st.selectbox("Select Student to Manage:", list(student_options.keys()))
        selected_student = student_options[selected_label]

        col_up, col_del = st.columns([2, 1])

        with col_up:
            st.markdown("##### Update Details")
            with st.form("edit_student_form"):
                up_name = st.text_input("Full Name", value=selected_student["name"])
                up_email = st.text_input("Email", value=selected_student["email"])
                
                dept_idx = departments.index(selected_student["department"]) if selected_student["department"] in departments else 0
                up_dept = st.selectbox("Department", departments, index=dept_idx)
                
                year_idx = academic_years.index(selected_student["year"]) if selected_student["year"] in academic_years else 0
                up_year = st.selectbox("Year", academic_years, index=year_idx)

                save_btn = st.form_submit_button("Save Changes", use_container_width=True)
                if save_btn:
                    update_student(selected_student["id"], up_name, up_email, up_dept, up_year)
                    st.success("Student details updated successfully!")
                    st.rerun()

        with col_del:
            st.markdown("##### Danger Zone")
            st.write(f"Remove **{selected_student['name']}** permanently from the system.")
            if st.button("🗑️ Delete Student", use_container_width=True):
                delete_student(selected_student["id"])
                st.warning(f"Student {selected_student['name']} deleted.")
                st.rerun()
    else:
        st.info("No students registered yet.")
