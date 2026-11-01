import streamlit as st
import pandas as pd
from database import (
    get_all_students, 
    get_connection, 
    delete_single_mark, 
    delete_all_marks_for_student
)

st.title("📝 Marks & Examination Records")
st.markdown("<p style='color: #94a3b8;'>Assign, view, export, and delete academic marks.</p>", unsafe_allow_html=True)
st.divider()

tab_add, tab_view, tab_delete = st.tabs(["➕ Assign Marks", "📋 Academic Records", "🗑️ Delete Marks"])

# ==========================================
# TAB 1: ASSIGN / ADD MARKS
# ==========================================
with tab_add:
    st.subheader("Enter Student Exam Score")
    students = get_all_students()

    if students:
        student_dict = {f"{s['roll_number']} - {s['name']} ({s['department']})": s["id"] for s in students}
        selected_student = st.selectbox("Select Student:", list(student_dict.keys()), key="assign_mark_student")
        student_id = student_dict[selected_student]

        with st.form("add_mark_form", clear_on_submit=True):
            col1, col2 = st.columns(2)
            with col1:
                subject_name = st.text_input("Course / Subject Name *", placeholder="e.g. Thermodynamics / Python")
            with col2:
                marks_scored = st.number_input("Marks Obtained (0 - 100) *", min_value=0.0, max_value=100.0, value=75.0, step=1.0)

            if st.form_submit_button("Record Marks", use_container_width=True):
                if not subject_name.strip():
                    st.error("Please enter a valid subject name.")
                else:
                    with get_connection() as conn:
                        cursor = conn.cursor()
                        cursor.execute(
                            "INSERT INTO marks (student_id, subject, marks) VALUES (?, ?, ?)",
                            (student_id, subject_name.strip(), float(marks_scored))
                        )
                        conn.commit()
                    st.success(f"Recorded {marks_scored} marks in {subject_name.strip()}!")
                    st.rerun()
    else:
        st.info("No registered students found.")

# ==========================================
# TAB 2: VIEW & DOWNLOAD MARKS
# ==========================================
with tab_view:
    st.subheader("📋 Student Academic Records")

    with get_connection() as conn:
        records_df = pd.read_sql_query("""
            SELECT 
                s.roll_number AS "Roll Number",
                s.name AS "Student Name",
                s.department AS "Department",
                m.subject AS "Subject",
                m.marks AS "Marks",
                CASE WHEN m.marks >= 40 THEN 'Pass' ELSE 'Fail' END AS "Result",
                CASE 
                    WHEN m.marks >= 90 THEN 'O'
                    WHEN m.marks >= 80 THEN 'A+'
                    WHEN m.marks >= 70 THEN 'A'
                    WHEN m.marks >= 60 THEN 'B+'
                    WHEN m.marks >= 50 THEN 'B'
                    WHEN m.marks >= 40 THEN 'C'
                    ELSE 'F'
                END AS "Grade"
            FROM marks m
            JOIN students s ON m.student_id = s.id
            ORDER BY s.roll_number, m.subject
        """, conn)

    if not records_df.empty:
        st.dataframe(records_df, use_container_width=True, hide_index=True)
        csv_data = records_df.to_csv(index=False).encode("utf-8")
        st.download_button("⬇ Download Marks CSV", csv_data, "academic_records.csv", "text/csv")[cite: 9]
    else:
        st.info("No academic marks recorded in the database yet.")

# ==========================================
# TAB 3: PERMANENTLY DELETE MARKS
# ==========================================
with tab_delete:
    st.subheader("🗑️ Permanently Remove Marks")
    st.warning("⚠️ Deleting marks will remove them permanently from the database and update student transcripts immediately.")

    with get_connection() as conn:
        marks_with_ids = pd.read_sql_query("""
            SELECT 
                m.id AS mark_id,
                s.id AS student_id,
                s.roll_number,
                s.name,
                s.department,
                m.subject,
                m.marks
            FROM marks m
            JOIN students s ON m.student_id = s.id
            ORDER BY s.roll_number, m.subject
        """, conn)

    if not marks_with_ids.empty:
        col_single, col_bulk = st.columns(2)

        # 1. Delete a Single Mark Record
        with col_single:
            st.markdown("##### 1. Delete Single Subject Entry")
            options = {
                f"{r['roll_number']} | {r['name']} — {r['subject']} ({r['marks']} marks) [ID: {r['mark_id']}]": int(r['mark_id'])
                for _, r in marks_with_ids.iterrows()
            }
            selected_option = st.selectbox("Select Record to Delete:", list(options.keys()))
            selected_mark_id = options[selected_option]

            if st.button("🗑️ Delete Selected Entry", use_container_width=True):
                delete_single_mark(selected_mark_id)
                st.success("Record deleted permanently from database!")
                st.rerun()

        # 2. Clear All Marks for a Specific Student
        with col_bulk:
            st.markdown("##### 2. Clear All Marks for a Student")
            student_options = {
                f"{s['roll_number']} - {s['name']} ({s['department']})": int(s["student_id"])
                for _, s in marks_with_ids.drop_duplicates(subset=["student_id"]).iterrows()
            }
            selected_st_label = st.selectbox("Select Student:", list(student_options.keys()))
            target_student_id = student_options[selected_st_label]

            if st.button("⚠️ Clear All Marks for Selected Student", use_container_width=True):
                delete_all_marks_for_student(target_student_id)
                st.success("All mark records permanently deleted!")
                st.rerun()

    else:
        st.info("No marks entries available to delete.")
