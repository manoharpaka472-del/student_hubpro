import streamlit as st
import pandas as pd
import plotly.express as px
import os

from database import (
    get_all_students,
    get_dashboard_stats,
    get_connection,
    update_student_password,
    add_announcement,
    get_announcements,
    mark_student_attendance,
    get_student_attendance_summary,
    get_student_attendance_records,
    add_assignment,
    get_assignments_for_department,
    submit_assignment,
    get_submissions_for_assignment,
    grade_submission,
    add_timetable_entry,
    get_timetable,
    add_fee_due,
    get_student_fees,
    submit_feedback,
    get_all_feedback
)
from auth import require_login, logout_button

# ==========================================
# PAGE CONFIGURATION
# ==========================================
st.set_page_config(
    page_title="Academic Atelier | Portal",
    page_icon="🏛️",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.session_state["_logout_rendered"] = False

# ==========================================
# MODERN CAMPUS BACKGROUND & VIBRANT 3D BUTTONS
# ==========================================
st.markdown("""
<style>
    /* Architectural Campus Photo Background with Deep Mesh Blend */
    .stApp {
        background: linear-gradient(rgba(10, 15, 30, 0.86), rgba(15, 23, 42, 0.94)),
                    url("https://images.unsplash.com/photo-1541339907198-e08756dedf3f?q=80&w=2070&auto=format&fit=crop") no-repeat center center fixed !important;
        background-size: cover !important;
        color: #f8fafc !important;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Inter", sans-serif;
    }

    h1, h2, h3, h4 {
        color: #ffffff !important;
        font-weight: 800 !important;
        letter-spacing: -0.5px;
        text-shadow: 0 2px 8px rgba(0, 0, 0, 0.5);
    }
    p, span, label, .stMarkdown {
        color: #e2e8f0 !important;
    }

    /* Translucent Glassmorphism Sidebar */
    [data-testid="stSidebar"] {
        background: rgba(11, 19, 43, 0.92) !important;
        backdrop-filter: blur(16px) !important;
        border-right: 1px solid rgba(56, 189, 248, 0.25) !important;
    }
    [data-testid="stSidebar"] * {
        color: #f1f5f9 !important;
    }

    /* Vibrant 3D Buttons with Neon Shadow */
    .stButton>button {
        width: 100%;
        background: linear-gradient(135deg, #1d4ed8 0%, #2563eb 50%, #0284c7 100%) !important;
        color: #ffffff !important;
        font-weight: 700 !important;
        font-size: 14px !important;
        border: 1px solid rgba(147, 197, 253, 0.45) !important;
        border-radius: 12px !important;
        padding: 12px 18px !important;
        margin-bottom: 8px !important;
        box-shadow: 0 6px 16px -2px rgba(37, 99, 235, 0.6), inset 0 1px 0 rgba(255, 255, 255, 0.3) !important;
        transition: all 0.22s cubic-bezier(0.4, 0, 0.2, 1) !important;
        transform: perspective(600px) translateZ(0);
        text-shadow: 0 1px 2px rgba(0, 0, 0, 0.4);
    }
    .stButton>button:hover {
        background: linear-gradient(135deg, #0284c7 0%, #06b6d4 100%) !important;
        color: #ffffff !important;
        transform: perspective(600px) translateY(-3px) scale(1.02);
        box-shadow: 0 12px 24px -2px rgba(6, 182, 212, 0.7), 0 0 18px rgba(56, 189, 248, 0.6), inset 0 1px 0 rgba(255, 255, 255, 0.6) !important;
        border-color: #ffffff !important;
    }
    .stButton>button:active {
        transform: perspective(600px) translateY(2px) scale(0.98);
        box-shadow: 0 2px 6px rgba(0, 0, 0, 0.7) !important;
    }

    /* Glass Cards */
    .figma-card {
        background: rgba(15, 23, 42, 0.82) !important;
        border: 1px solid rgba(56, 189, 248, 0.2) !important;
        border-radius: 16px !important;
        padding: 22px !important;
        box-shadow: 0 12px 32px rgba(0, 0, 0, 0.4) !important;
        backdrop-filter: blur(12px) !important;
        margin-bottom: 20px;
    }

    /* Metric Cards */
    div[data-testid="stMetric"] {
        background: linear-gradient(135deg, rgba(30, 41, 59, 0.85), rgba(15, 23, 42, 0.95)) !important;
        border: 1px solid rgba(56, 189, 248, 0.3) !important;
        padding: 20px 22px !important;
        border-radius: 16px !important;
        box-shadow: 0 8px 24px rgba(0, 0, 0, 0.5) !important;
        backdrop-filter: blur(10px);
    }
    div[data-testid="stMetricLabel"] p {
        color: #94a3b8 !important;
        font-size: 13px !important;
        font-weight: 700 !important;
        letter-spacing: 0.5px;
        text-transform: uppercase;
    }
    div[data-testid="stMetricValue"] div {
        color: #38bdf8 !important;
        font-size: 32px !important;
        font-weight: 800 !important;
        text-shadow: 0 0 12px rgba(56, 189, 248, 0.4);
    }

    /* Action Required Card */
    .action-required-card {
        background: rgba(124, 45, 18, 0.4) !important;
        border: 1px solid rgba(251, 146, 60, 0.5) !important;
        border-radius: 12px;
        padding: 16px;
        margin-top: 15px;
    }
    .action-required-title {
        color: #fb923c !important;
        font-weight: 800;
        font-size: 14px;
        margin-bottom: 6px;
    }
    .action-required-desc {
        color: #fdba74 !important;
        font-size: 13px;
        line-height: 1.4;
    }

    /* Activity Rows */
    .activity-row {
        display: flex;
        align-items: center;
        padding: 12px 0;
        border-bottom: 1px solid rgba(255, 255, 255, 0.08);
    }
    .activity-icon {
        width: 38px;
        height: 38px;
        border-radius: 10px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 18px;
        margin-right: 14px;
    }

    /* Institutional Glowing Banner */
    .institutional-banner {
        background: linear-gradient(135deg, #1e3a8a 0%, #2563eb 50%, #0284c7 100%);
        border: 1px solid rgba(255, 255, 255, 0.25);
        border-radius: 16px;
        padding: 32px;
        color: #ffffff;
        margin-top: 24px;
        box-shadow: 0 12px 32px rgba(37, 99, 235, 0.4);
    }

    /* Input & Table styling */
    .stTextInput input, .stSelectbox select, .stTextArea textarea, .stDateInput input, .stNumberInput input {
        background-color: rgba(15, 23, 42, 0.85) !important;
        color: #f8fafc !important;
        border: 1px solid rgba(56, 189, 248, 0.3) !important;
        border-radius: 10px !important;
    }
    .stTextInput input:focus, .stSelectbox select:focus, .stTextArea textarea:focus {
        border-color: #38bdf8 !important;
        box-shadow: 0 0 10px rgba(56, 189, 248, 0.4) !important;
    }
</style>
""", unsafe_allow_html=True)

# Authentication enforcement
require_login()

user_role = st.session_state.get("role", "admin")

if "current_page" not in st.session_state:
    st.session_state.current_page = "Dashboard" if user_role == "admin" else "My Academic Profile"


# ==========================================
# SIDEBAR NAVIGATION
# ==========================================
logout_button()

st.sidebar.markdown("""
<div style="padding: 10px 0 15px 0; border-bottom: 1px solid rgba(255,255,255,0.1); margin-bottom: 15px;">
    <h3 style="margin:0; font-size: 20px; font-weight: 800; color: #ffffff;">Academic Atelier</h3>
    <span style="font-size: 11px; font-weight: 700; color: #38bdf8; letter-spacing: 0.8px;">INSTITUTIONAL PORTAL</span>
</div>
""", unsafe_allow_html=True)

if user_role == "admin":
    st.sidebar.caption("MAIN CONTROLS")

    if st.sidebar.button("📊  Executive Dashboard", use_container_width=True):
        st.session_state.current_page = "Dashboard"
        st.rerun()

    if st.sidebar.button("👨‍🎓  Student Directory", use_container_width=True):
        st.session_state.current_page = "Students"
        st.rerun()

    if st.sidebar.button("📅  Attendance Registry", use_container_width=True):
        st.session_state.current_page = "Attendance"
        st.rerun()

    if st.sidebar.button("📚  Course Results & Marks", use_container_width=True):
        st.session_state.current_page = "Courses & Marks"
        st.rerun()

    if st.sidebar.button("📂  Assignments Hub", use_container_width=True):
        st.session_state.current_page = "Assignments"
        st.rerun()

    if st.sidebar.button("🗓️  Lecture Timetable", use_container_width=True):
        st.session_state.current_page = "Timetable"
        st.rerun()

    if st.sidebar.button("💳  Fee Management", use_container_width=True):
        st.session_state.current_page = "Fees"
        st.rerun()

    if st.sidebar.button("⭐  Course Evaluations", use_container_width=True):
        st.session_state.current_page = "Feedback"
        st.rerun()

    if st.sidebar.button("📢  Announcements", use_container_width=True):
        st.session_state.current_page = "Announcements"
        st.rerun()

    st.sidebar.divider()
    try:
        with open("students.db", "rb") as db_file:
            st.sidebar.download_button(
                label="💾 Backup Database (.db)",
                data=db_file,
                file_name="academic_atelier_backup.db",
                mime="application/x-sqlite3",
                use_container_width=True
            )
    except FileNotFoundError:
        pass

else:
    student = st.session_state.get("student_info", {})
    st.sidebar.caption("STUDENT PORTAL")
    st.sidebar.markdown(f"**{student.get('name', 'Student')}**")
    st.sidebar.caption(f"Roll: `{student.get('roll_number', '')}`")

    if st.sidebar.button("🎓  Dashboard & Profile", use_container_width=True):
        st.session_state.current_page = "My Academic Profile"
        st.rerun()

    if st.sidebar.button("📅  My Attendance Status", use_container_width=True):
        st.session_state.current_page = "My Attendance"
        st.rerun()

    if st.sidebar.button("📂  Coursework & Projects", use_container_width=True):
        st.session_state.current_page = "Student Assignments"
        st.rerun()

    if st.sidebar.button("🗓️  Weekly Schedule", use_container_width=True):
        st.session_state.current_page = "Student Timetable"
        st.rerun()

    if st.sidebar.button("💳  Fee Clearance", use_container_width=True):
        st.session_state.current_page = "Student Fees"
        st.rerun()

    if st.sidebar.button("📝  Grades & Transcript", use_container_width=True):
        st.session_state.current_page = "My Marks"
        st.rerun()

    if st.sidebar.button("🛠️  Academic Toolkit (CGPA)", use_container_width=True):
        st.session_state.current_page = "Academic Tools"
        st.rerun()

    if st.sidebar.button("⭐  Course Evaluation", use_container_width=True):
        st.session_state.current_page = "Student Feedback"
        st.rerun()

    if st.sidebar.button("🔒  Security & Password", use_container_width=True):
        st.session_state.current_page = "Account Security"
        st.rerun()


def render_page(filename_variations):
    current_dir = os.path.dirname(os.path.abspath(__file__))
    candidates = []
    for fname in filename_variations:
        candidates.append(os.path.join(current_dir, "pages", fname))
        candidates.append(os.path.join(current_dir, fname))
        candidates.append(os.path.join("pages", fname))
        candidates.append(fname)
        
    found_path = next((p for p in candidates if os.path.exists(p)), None)
    if found_path:
        with open(found_path, "r", encoding="utf-8") as f:
            code = f.read()
            exec(code, globals())
    else:
        st.error(f"Module file not found: {filename_variations[0]}.")


# ==========================================
# ADMIN PAGE ROUTING
# ==========================================
if user_role == "admin":
    if st.session_state.current_page == "Dashboard":
        st.markdown("""
        <div style="margin-bottom: 24px;">
            <h1 style="font-size: 28px; font-weight: 800; color: #ffffff; margin-bottom: 4px;">Welcome back, Admin</h1>
            <p style="color: #94a3b8; font-size: 15px; margin: 0;">Campus performance summary and real-time operations.</p>
        </div>
        """, unsafe_allow_html=True)

        stats = get_dashboard_stats()
        students = get_all_students()

        c1, c2, c3 = st.columns(3)
        with c1:
            st.metric(label="TOTAL ENROLLED STUDENTS", value=f"{stats['total_students']:,}", delta="+4% this term")
        with c2:
            st.metric(label="ACTIVE DEPARTMENTS", value=stats["total_departments"], delta="Verified")
        with c3:
            st.metric(label="OVERALL PASS RATE", value=f"{stats['pass_percentage']:.1f}%", delta=f"{stats['average_marks']:.1f}% Avg Score")

        st.write("")

        col_left, col_right = st.columns([2, 1])

        with col_left:
            st.markdown("""
            <div class="figma-card">
                <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom: 14px;">
                    <h3 style="font-size: 17px; font-weight: 700; color: #ffffff; margin: 0;">Recent Activities</h3>
                    <span style="font-size: 13px; color: #38bdf8; font-weight: 700;">Live Feed</span>
                </div>
            """, unsafe_allow_html=True)

            notices = get_announcements()
            if students:
                latest_student = students[-1]
                st.markdown(f"""
                <div class="activity-row">
                    <div class="activity-icon" style="background-color: rgba(37, 99, 235, 0.2); color: #60a5fa;">👤</div>
                    <div>
                        <div style="font-size: 14px; font-weight: 600; color: #f8fafc;">New student enrolled</div>
                        <div style="font-size: 12px; color: #94a3b8;">{latest_student['name']} ({latest_student['roll_number']}) — {latest_student['department']} department</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

            st.markdown("""
                <div class="activity-row">
                    <div class="activity-icon" style="background-color: rgba(217, 119, 6, 0.2); color: #fbbf24;">📅</div>
                    <div>
                        <div style="font-size: 14px; font-weight: 600; color: #f8fafc;">Daily attendance synchronized</div>
                        <div style="font-size: 12px; color: #94a3b8;">Attendance records published to student portals</div>
                    </div>
                </div>
            """, unsafe_allow_html=True)

            if notices:
                st.markdown(f"""
                <div class="activity-row">
                    <div class="activity-icon" style="background-color: rgba(147, 51, 234, 0.2); color: #c084fc;">📢</div>
                    <div>
                        <div style="font-size: 14px; font-weight: 600; color: #f8fafc;">{notices[0][0]}</div>
                        <div style="font-size: 12px; color: #94a3b8;">{notices[0][1][:65]}...</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

            st.markdown("</div>", unsafe_allow_html=True)

            # Performance Warning
            st.markdown("""
            <div class="figma-card">
                <h3 style="font-size: 17px; font-weight: 700; color: #ffffff; margin: 0 0 12px 0;">Academic Intervention Roster</h3>
            """, unsafe_allow_html=True)
            with get_connection() as conn:
                marks_all = pd.read_sql_query("""
                    SELECT s.roll_number, s.name, s.department, AVG(m.marks) as avg_marks,
                           SUM(CASE WHEN m.marks < 40 THEN 1 ELSE 0 END) as failed_subjects
                    FROM students s
                    INNER JOIN marks m ON s.id = m.student_id
                    GROUP BY s.id
                """, conn)

            if not marks_all.empty:
                at_risk = marks_all[(marks_all["avg_marks"] < 50) | (marks_all["failed_subjects"] > 0)]
                if not at_risk.empty:
                    st.dataframe(at_risk.rename(columns={
                        "roll_number": "Roll No", "name": "Student Name",
                        "department": "Department", "avg_marks": "Average",
                        "failed_subjects": "Backlogs"
                    }).round({"Average": 1}), use_container_width=True, hide_index=True)
                else:
                    st.success("✅ All enrolled students meet academic standing criteria.")
            else:
                st.info("Performance stats will calculate automatically when marks are entered.")
            st.markdown("</div>", unsafe_allow_html=True)

        with col_right:
            st.markdown("""
            <div class="figma-card">
                <h3 style="font-size: 17px; font-weight: 700; color: #ffffff; margin: 0 0 14px 0;">Quick Actions</h3>
            """, unsafe_allow_html=True)

            if st.button("➕ Add New Student", key="qa_add_st", use_container_width=True):
                st.session_state.current_page = "Students"
                st.rerun()

            if st.button("📅 Mark Class Attendance", key="qa_att", use_container_width=True):
                st.session_state.current_page = "Attendance"
                st.rerun()

            if st.button("📂 Create Assignment", key="qa_assign", use_container_width=True):
                st.session_state.current_page = "Assignments"
                st.rerun()

            st.markdown("""
                <div class="action-required-card">
                    <div class="action-required-title">! Action Required</div>
                    <div class="action-required-desc">
                        End-of-term attendance reviews require validation. Flagged students with &lt; 75% attendance need clearance before admit cards unlock.
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)

        # Institutional Banner
        st.markdown("""
        <div class="institutional-banner">
            <h2 style="font-size: 22px; font-weight: 800; margin: 0 0 8px 0; color: #ffffff;">Upgrading Campus Infrastructure for 2026</h2>
            <p style="color: #e0f2fe; font-size: 14px; max-width: 650px; line-height: 1.5; margin-bottom: 20px;">
                Centralized academic portals, live marks recording, and dynamic student toolkits are now operational across all departments.
            </p>
            <span style="background-color: #ffffff; color: #1e3a8a; font-weight: 800; padding: 10px 22px; border-radius: 8px; font-size: 13px; display: inline-block;">
                System Status: Online
            </span>
        </div>
        """, unsafe_allow_html=True)

    elif st.session_state.current_page == "Students":
        render_page(["Student_Management.py", "1_Student_Management.py", "3_Student_Management.py"])

    elif st.session_state.current_page == "Attendance":
        st.title("📅 Attendance Registry")
        st.markdown("<p style='color: #94a3b8;'>Record daily student attendance by department and subject.</p>", unsafe_allow_html=True)

        col_a1, col_a2, col_a3 = st.columns(3)
        with col_a1:
            att_date = st.date_input("Session Date")
        with col_a2:
            dept_filter = st.selectbox("Department", ["All", "Mechanical", "Computer Science", "Electrical", "Civil", "Electronics", "Information Technology"])
        with col_a3:
            subject_name = st.text_input("Course Subject", placeholder="e.g. Thermodynamics")

        students_pool = get_all_students()
        if dept_filter != "All":
            students_pool = [s for s in students_pool if s["department"] == dept_filter]

        if not students_pool:
            st.info("No students found in the selected department.")
        elif not subject_name.strip():
            st.warning("Please specify a course subject name.")
        else:
            with st.form("attendance_form"):
                st.write(f"Marking attendance for **{len(students_pool)} student(s)**:")
                status_dict = {}
                for s in students_pool:
                    c1, c2 = st.columns([3, 1])
                    c1.markdown(f"**{s['name']}** (`{s['roll_number']}`) — *{s['department']}*")
                    status_dict[s["id"]] = c2.checkbox("Present", value=True, key=f"att_{s['id']}")
                
                if st.form_submit_button("Save Attendance Session", use_container_width=True):
                    date_str = att_date.strftime("%Y-%m-%d")
                    for s_id, is_present in status_dict.items():
                        mark_student_attendance(s_id, subject_name.strip(), date_str, "Present" if is_present else "Absent")
                    st.success("✅ Attendance saved successfully!")

    elif st.session_state.current_page == "Courses & Marks":
        render_page(["Marks_Management.py", "2_Marks_Management.py", "Course_Management.py"])

    elif st.session_state.current_page == "Assignments":
        st.title("📂 Assignments Desk")
        tab1, tab2 = st.tabs(["➕ Post Assignment", "📝 Review Submissions"])
        with tab1:
            with st.form("new_assign_form"):
                a_title = st.text_input("Assignment Title")
                a_sub = st.text_input("Subject")
                a_dept = st.selectbox("Target Department", ["All", "Mechanical", "Computer Science", "Electrical", "Civil", "Electronics", "Information Technology"])
                a_due = st.date_input("Deadline")
                a_desc = st.text_area("Instructions")
                if st.form_submit_button("Post Assignment", use_container_width=True):
                    if a_title and a_sub and a_desc:
                        add_assignment(a_title, a_sub, a_dept, str(a_due), a_desc)
                        st.success("Assignment published!")
        with tab2:
            with get_connection() as conn:
                assignments_df = pd.read_sql_query("SELECT id, title, subject FROM assignments ORDER BY id DESC", conn)
            if not assignments_df.empty:
                assign_dict = {f"#{row['id']} - {row['title']} ({row['subject']})": row['id'] for _, row in assignments_df.iterrows()}
                chosen_a = st.selectbox("Select Assignment:", list(assign_dict.keys()))
                submissions = get_submissions_for_assignment(assign_dict[chosen_a])
                if submissions:
                    for sub in submissions:
                        with st.expander(f"{sub['name']} ({sub['roll_number']}) — Grade: {sub['grade']}"):
                            st.write(f"Link: [{sub['submission_link']}]({sub['submission_link']})")
                            with st.form(f"g_{sub['id']}"):
                                g = st.selectbox("Assign Grade", ["A+", "A", "B", "C", "Fail"], key=f"sel_{sub['id']}")
                                if st.form_submit_button("Submit Grade"):
                                    grade_submission(sub['id'], g)
                                    st.success("Grade saved!")
                                    st.rerun()
                else:
                    st.info("No submissions yet.")

    elif st.session_state.current_page == "Timetable":
        st.title("🗓️ Department Timetable")
        with st.form("tt_form"):
            col1, col2 = st.columns(2)
            with col1:
                t_dept = st.selectbox("Department", ["Mechanical", "Computer Science", "Electrical", "Civil", "Electronics", "Information Technology"])
                t_year = st.selectbox("Year", [1, 2, 3, 4])
                t_day = st.selectbox("Day", ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"])
            with col2:
                t_slot = st.text_input("Time Slot (e.g. 09:30 AM - 10:30 AM)")
                t_sub = st.text_input("Subject")
                t_room = st.text_input("Room No", placeholder="e.g. ME-204")
            if st.form_submit_button("Add Schedule Entry", use_container_width=True):
                if t_slot and t_sub and t_room:
                    add_timetable_entry(t_dept, t_year, t_day, t_slot, t_sub, t_room)
                    st.success("Schedule slot saved!")

    elif st.session_state.current_page == "Fees":
        st.title("💳 Fees & Accounts")
        tab1, tab2 = st.tabs(["➕ Assign Fee Due", "📋 All Records"])
        with tab1:
            students_all = get_all_students()
            if students_all:
                st_map = {f"{s['roll_number']} - {s['name']}": s['id'] for s in students_all}
                sel = st.selectbox("Select Student:", list(st_map.keys()))
                f_type = st.selectbox("Fee Type", ["Semester Tuition", "Exam Fee", "Library Due", "Hostel Fee"])
                f_amt = st.number_input("Amount (INR)", min_value=100.0, step=500.0, value=25000.0)
                f_due = st.date_input("Due Date")
                if st.button("Generate Invoice", use_container_width=True):
                    add_fee_due(st_map[sel], f_type, f_amt, str(f_due))
                    st.success("Invoice generated!")
        with tab2:
            with get_connection() as conn:
                fees_df = pd.read_sql_query("SELECT s.roll_number, s.name, f.fee_type, f.amount, f.due_date, f.status FROM fee_dues f JOIN students s ON f.student_id = s.id ORDER BY f.id DESC", conn)
            st.dataframe(fees_df, use_container_width=True, hide_index=True)

    elif st.session_state.current_page == "Feedback":
        st.title("⭐ Course & Faculty Feedback")
        feedbacks = get_all_feedback()
        if feedbacks:
            st.dataframe(pd.DataFrame(feedbacks), use_container_width=True, hide_index=True)
        else:
            st.info("No feedback submitted yet.")

    elif st.session_state.current_page == "Announcements":
        st.title("📢 Campus Announcements")
        with st.form("notice_form"):
            n_t = st.text_input("Title")
            n_m = st.text_area("Message")
            if st.form_submit_button("Broadcast Notice", use_container_width=True):
                if n_t and n_m:
                    add_announcement(n_t, n_m)
                    st.success("Broadcast published!")


# ==========================================
# STUDENT PAGE ROUTING
# ==========================================
else:
    student = st.session_state.get("student_info", {})
    student_id = student.get("id")

    with get_connection() as conn:
        marks_df = pd.read_sql_query("SELECT subject, marks FROM marks WHERE student_id = ? ORDER BY subject", conn, params=(student_id,))

    if st.session_state.current_page == "My Academic Profile":
        st.markdown(f"""
        <div style="margin-bottom: 20px;">
            <h1 style="font-size: 28px; font-weight: 800; color: #ffffff; margin-bottom: 4px;">Welcome back, {student.get('name', 'Student')}</h1>
            <p style="color: #94a3b8; font-size: 15px; margin: 0;">Institutional Candidate Dashboard</p>
        </div>
        """, unsafe_allow_html=True)

        col1, col2 = st.columns([1, 2])
        with col1:
            st.markdown(f"""
            <div class="figma-card">
                <h3 style="margin-top:0; color: #ffffff;">{student.get('name')}</h3>
                <p style="color: #38bdf8; font-weight: 800; font-size: 16px; margin-bottom: 12px;">Roll: {student.get('roll_number')}</p>
                <hr style="border: 0.5px solid rgba(255,255,255,0.1); margin: 12px 0;">
                <p style="font-size:14px; margin:6px 0;"><strong>Department:</strong> {student.get('department')}</p>
                <p style="font-size:14px; margin:6px 0;"><strong>Academic Year:</strong> Year {student.get('year')}</p>
                <p style="font-size:14px; margin:6px 0;"><strong>Email:</strong> {student.get('email')}</p>
                <p style="font-size:14px; margin:6px 0;"><strong>Status:</strong> <span style="color:#34d399; font-weight:700;">Active Enrolled</span></p>
            </div>
            """, unsafe_allow_html=True)

            with st.expander("🪪 View Exam Admit Card"):
                st.markdown(f"""
                <div style="background: rgba(15, 23, 42, 0.95); border: 2px solid #38bdf8; border-radius: 12px; padding: 18px; box-shadow: 0 8px 24px rgba(56,189,248,0.25);">
                    <div style="text-align: center; border-bottom: 1px solid rgba(255,255,255,0.1); padding-bottom: 8px;">
                        <h4 style="color: #38bdf8; margin: 0;">ACADEMIC ATELIER</h4>
                        <p style="color: #94a3b8; font-size: 11px; margin: 0;">SEMESTER EXAMINATION ADMIT CARD</p>
                    </div>
                    <div style="display: flex; justify-content: space-between; margin-top: 14px; font-size: 13px;">
                        <div>
                            <p style="margin:4px 0;"><strong>Name:</strong> {student.get('name')}</p>
                            <p style="margin:4px 0;"><strong>Roll:</strong> <span style="color:#38bdf8;">{student.get('roll_number')}</span></p>
                            <p style="margin:4px 0;"><strong>Dept:</strong> {student.get('department')}</p>
                            <p style="margin:4px 0;"><strong>Year:</strong> Year {student.get('year')}</p>
                        </div>
                        <div style="border: 1px dashed #64748b; width: 80px; height: 100px; display:flex; align-items:center; justify-content:center; border-radius: 6px;">
                            <span style="font-size: 10px; color:#94a3b8;">Photo</span>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

        with col2:
            st.markdown("""
            <div class="figma-card">
                <h3 style="font-size: 17px; font-weight: 700; color: #ffffff; margin: 0 0 12px 0;">Institutional Bulletins</h3>
            """, unsafe_allow_html=True)
            notices = get_announcements()
            if notices:
                for title, msg, dt in notices:
                    st.markdown(f"""
                    <div style="border-bottom: 1px solid rgba(255,255,255,0.08); padding: 10px 0;">
                        <div style="display:flex; justify-content:space-between;">
                            <strong style="color:#38bdf8;">📌 {title}</strong>
                            <span style="font-size:12px; color:#94a3b8;">{dt}</span>
                        </div>
                        <p style="font-size:13px; color:#cbd5e1; margin: 4px 0 0 0;">{msg}</p>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.info("No active notices.")
            st.markdown("</div>", unsafe_allow_html=True)

    elif st.session_state.current_page == "My Attendance":
        st.title("📅 My Attendance Status")
        summary = get_student_attendance_summary(student_id)
        if summary:
            df = pd.DataFrame(summary)
            df["Percentage"] = (df["attended_classes"] / df["total_classes"]) * 100
            df["Status"] = df["Percentage"].apply(lambda x: "Eligible (>= 75%) ✅" if x >= 75 else "Shortage (< 75%) ⚠️")
            st.dataframe(df.rename(columns={
                "subject": "Course", "total_classes": "Conducted", "attended_classes": "Attended", "Percentage": "Attendance %"
            }).round({"Attendance %": 1}), use_container_width=True, hide_index=True)
        else:
            st.info("No attendance recorded yet.")

    elif st.session_state.current_page == "Student Assignments":
        st.title("📂 Course Assignments")
        assignments = get_assignments_for_department(student.get("department"))
        if assignments:
            for a in assignments:
                with st.expander(f"📌 {a['title']} — {a['subject']} (Due: {a['deadline']})"):
                    st.write(a['description'])
                    with st.form(f"sub_{a['id']}"):
                        lnk = st.text_input("Submission URL (Drive / GitHub)")
                        if st.form_submit_button("Submit Work"):
                            submit_assignment(a['id'], student_id, lnk)
                            st.success("Submitted successfully!")
        else:
            st.info("No assignments posted.")

    elif st.session_state.current_page == "Student Timetable":
        st.title("🗓️ Weekly Schedule")
        tt = get_timetable(student.get("department"), student.get("year"))
        if tt:
            st.dataframe(pd.DataFrame(tt).rename(columns={
                "day_of_week": "Day", "time_slot": "Time", "subject": "Subject", "room_no": "Room"
            }), use_container_width=True, hide_index=True)
        else:
            st.info("Timetable not available yet.")

    elif st.session_state.current_page == "Student Fees":
        st.title("💳 Fee Clearance Status")
        fees = get_student_fees(student_id)
        if fees:
            st.dataframe(pd.DataFrame(fees).rename(columns={
                "fee_type": "Fee Description", "amount": "Amount (INR)", "due_date": "Due Date", "status": "Status"
            }), use_container_width=True, hide_index=True)
        else:
            st.success("✅ All fees cleared.")

    elif st.session_state.current_page == "My Marks":
        st.title("📝 Semester Examination Transcript")
        if not marks_df.empty:
            st.dataframe(marks_df.rename(columns={"subject": "Subject", "marks": "Marks (100)"}), use_container_width=True, hide_index=True)
        else:
            st.info("No marks posted yet.")

    elif st.session_state.current_page == "Academic Tools":
        st.title("🛠️ Academic Planning Tools")
        tab1, tab2 = st.tabs(["📊 Cumulative CGPA", "📅 Attendance Margin"])
        with tab1:
            num = st.slider("Completed Semesters", 1, 8, 3)
            s_list = []
            cols = st.columns(min(num, 4))
            for i in range(num):
                with cols[i % 4]:
                    sg = st.number_input(f"Sem {i+1} SGPA", 0.0, 10.0, 8.0, 0.05, key=f"sg_{i}")
                    cr = st.number_input(f"Sem {i+1} Credits", 10, 30, 20, 1, key=f"cr_{i}")
                    s_list.append((sg, cr))
            if s_list:
                cg = sum(s * c for s, c in s_list) / sum(c for _, c in s_list)
                st.metric("Overall CGPA", f"{cg:.2f} / 10.0")
        with tab2:
            t = st.number_input("Total Scheduled Classes", 1, value=60)
            a = st.number_input("Attended Classes", 0, int(t), value=50)
            pct = (a / t) * 100
            st.metric("Attendance", f"{pct:.1f}%")
            if pct >= 75:
                st.success(f"Safe! You can miss up to {int((a - 0.75 * t) / 0.75)} more classes.")
            else:
                st.error(f"Deficit! You must attend {int((0.75 * t - a) / 0.25)} consecutive classes.")

    elif st.session_state.current_page == "Student Feedback":
        st.title("⭐ Course Feedback")
        with st.form("fb_form"):
            c_name = st.text_input("Course / Instructor")
            r = st.slider("Rating", 1, 5, 5)
            c = st.text_area("Feedback Comments")
            if st.form_submit_button("Submit Anonymous Feedback"):
                submit_feedback(student_id, c_name, r, c)
                st.success("Feedback submitted!")

    elif st.session_state.current_page == "Account Security":
        st.title("🔒 Change Password")
        with st.form("pwd_form"):
            old_p = st.text_input("Current Password", type="password")
            new_p = st.text_input("New Password", type="password")
            con_p = st.text_input("Confirm Password", type="password")
            if st.form_submit_button("Update Password"):
                curr = (student.get("password") or "student123").strip()
                if old_p.strip() != curr:
                    st.error("Current password incorrect.")
                elif new_p.strip() != con_p.strip():
                    st.error("Passwords do not match.")
                elif len(new_p.strip()) < 4:
                    st.warning("Password too short.")
                else:
                    update_student_password(student["id"], new_p.strip())
                    st.session_state["student_info"]["password"] = new_p.strip()
                    st.success("Password updated successfully!")
