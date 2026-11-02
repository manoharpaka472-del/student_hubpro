import streamlit as st
import pandas as pd
from database import (
    get_all_students, 
    get_connection, 
    delete_single_mark, 
    delete_all_marks_for_student,
    update_single_mark
)

st.title("📝 Marks & Examination Records")
st.markdown("<p style='color: #94a3b8;'>Assign, view, export, update, and delete academic marks.</p>", unsafe_allow_html=True)
st.divider()

tab_add, tab_view, tab_manage = st.tabs(["➕ Assign Marks", "📋 Academic Records", "✏️ Update / Delete Marks"])

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
        st.info("No registered students found. Register students first in the Student Directory.")

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
        st.download_button("⬇ Download Marks CSV", csv_data, "academic_records.csv", "text/csv")
    else:
        st.info("No academic marks recorded in the database yet.")

# ==========================================
# TAB 3: UPDATE OR PERMANENTLY DELETE MARKS
# ==========================================
with tab_manage:
    st.subheader("✏️ Update or Remove Marks")

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
        options = {
            f"{r['roll_number']} | {r['name']} — {r['subject']} ({r['marks']} marks) [ID: {r['mark_id']}]": int(r['mark_id'])
            for _, r in marks_with_ids.iterrows()
        }

        col_edit, col_del = st.columns(2)

        # 1. Edit / Change Score
        with col_edit:
            st.markdown("##### 1. Edit / Correct Marks")
            sel_edit_label = st.selectbox("Select Record to Change:", list(options.keys()), key="edit_mark_select")
            sel_edit_id = options[sel_edit_label]
            new_val = st.number_input("New Score (0 - 100)", min_value=0.0, max_value=100.0, value=80.0, step=1.0)
            
            if st.button("💾 Update Score", use_container_width=True):
                update_single_mark(sel_edit_id, new_val)
                st.success("Marks updated successfully!")
                st.rerun()

        # 2. Delete Single Record
        with col_del:
            st.markdown("##### 2. Permanently Delete Mark")
            sel_del_label = st.selectbox("Select Record to Delete:", list(options.keys()), key="del_mark_select")
            sel_del_id = options[sel_del_label]

            if st.button("🗑️ Delete Selected Entry", use_container_width=True):
                delete_single_mark(sel_del_id)
                st.success("Record permanently removed!")
                st.rerun()

        st.divider()

        # 3. Clear All Marks for Student
        st.markdown("##### 3. Clear All Marks for a Specific Student")
        student_options = {
            f"{s['roll_number']} - {s['name']} ({s['department']})": int(s["student_id"])
            for _, s in marks_with_ids.drop_duplicates(subset=["student_id"]).iterrows()
        }
        selected_st_label = st.selectbox("Select Student:", list(student_options.keys()), key="clear_all_st_select")
        target_student_id = student_options[selected_st_label]

        if st.button("⚠️ Clear All Marks for This Student", use_container_width=True):
            delete_all_marks_for_student(target_student_id)
            st.success("All marks for the student have been cleared!")
            st.rerun()

    else:
        st.info("No marks entries available to edit or delete.")
