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
# FIGMA-INSPIRED CLEAN SAAS LIGHT THEME CSS
# ==========================================
st.markdown("""
<style>
    /* Clean SaaS Light Canvas */
    .stApp {
        background-color: #f8fafc !important;
        color: #0f172a !important;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Inter", sans-serif;
    }

    /* Clean White Sidebar */
    [data-testid="stSidebar"] {
        background-color: #ffffff !important;
        border-right: 1px solid #e2e8f0 !important;
    }
    [data-testid="stSidebar"] * {
        color: #334155 !important;
    }

    /* Sidebar Active & Navigation Buttons */
    .stButton>button {
        width: 100%;
        background-color: #ffffff !important;
        color: #334155 !important;
        font-weight: 600 !important;
        font-size: 14px !important;
        border: 1px solid #e2e8f0 !important;
        border-radius: 10px !important;
        padding: 10px 14px !important;
        margin-bottom: 6px !important;
        text-align: left !important;
        box-shadow: 0 1px 2px rgba(0, 0, 0, 0.04) !important;
        transition: all 0.2s ease-in-out !important;
    }
    .stButton>button:hover {
        background-color: #2563eb !important;
        color: #ffffff !important;
        border-color: #2563eb !important;
        transform: translateY(-1px);
        box-shadow: 0 4px 12px rgba(37, 99, 235, 0.25) !important;
    }
    .stButton>button:active {
        transform: translateY(1px);
    }

    /* Clean Figma Metric Cards */
    div[data-testid="stMetric"] {
        background-color: #ffffff !important;
        border: 1px solid #e2e8f0 !important;
        padding: 18px 22px !important;
        border-radius: 14px !important;
        box-shadow: 0 2px 4px rgba(0,0,0,0.03) !important;
    }
    div[data-testid="stMetricLabel"] p {
        color: #64748b !important;
        font-size: 12px !important;
        font-weight: 700 !important;
        letter-spacing: 0.5px;
        text-transform: uppercase;
    }
    div[data-testid="stMetricValue"] div {
        color: #0f172a !important;
        font-size: 28px !important;
        font-weight: 800 !important;
    }

    /* Custom White Containers / Panels */
    .figma-card {
        background-color: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 14px;
        padding: 22px;
        box-shadow: 0 2px 5px rgba(0, 0, 0, 0.03);
        margin-bottom: 20px;
    }

    /* Action Required Card */
    .action-required-card {
        background-color: #fff7ed;
        border: 1px solid #ffedd5;
        border-radius: 12px;
        padding: 16px;
        margin-top: 15px;
    }
    .action-required-title {
        color: #c2410c;
        font-weight: 700;
        font-size: 14px;
        margin-bottom: 6px;
    }
    .action-required-desc {
        color: #9a3412;
        font-size: 13px;
        line-height: 1.4;
    }

    /* Activity Item Row */
    .activity-row {
        display: flex;
        align-items: center;
        padding: 12px 0;
        border-bottom: 1px solid #f1f5f9;
    }
    .activity-icon {
        width: 36px;
        height: 36px;
        border-radius: 8px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 16px;
        margin-right: 12px;
    }

    /* Big Institutional Banner */
    .institutional-banner {
        background: linear-gradient(135deg, #1e3a8a 0%, #2563eb 50%, #38bdf8 100%);
        border-radius: 16px;
        padding: 32px;
        color: #ffffff;
        margin-top: 24px;
        box-shadow: 0 10px 25px -5px rgba(37, 99, 235, 0.3);
    }

    /* Dataframe Header styling */
    [data-testid="stDataFrame"] {
        border-radius: 12px !important;
        border: 1px solid #e2e8f0 !important;
        background-color: #ffffff !important;
    }
</style>
""", unsafe_allow_html=True)

# Authentication enforcement
require_login()

user_role = st.session_state.get("role", "admin")

if "current_page" not in st.session_state:
    st.session_state.current_page = "Dashboard" if user_role == "admin" else "My Academic Profile"


# ==========================================
# SIDEBAR NAVIGATION (FIGMA STYLE)
# ==========================================
logout_button()

st.sidebar.markdown("""
<div style="padding: 10px 0 15px 0; border-bottom: 1px solid #f1f5f9; margin-bottom: 15px;">
    <h3 style="margin:0; font-size: 18px; font-weight: 800; color: #0f172a;">Academic Atelier</h3>
    <span style="font-size: 11px; font-weight: 600; color: #64748b; letter-spacing: 0.5px;">INSTITUTIONAL PORTAL</span>
</div>
""", unsafe_allow_html=True)

if user_role == "admin":
    st.sidebar.caption("MAIN MENU")

    if st.sidebar.button("📊  Dashboard", use_container_width=True):
        st.session_state.current_page = "Dashboard"
        st.rerun()

    if st.sidebar.button("👨‍🎓  Students", use_container_width=True):
        st.session_state.current_page = "Students"
        st.rerun()

    if st.sidebar.button("📅  Attendance", use_container_width=True):
        st.session_state.current_page = "Attendance"
        st.rerun()

    if st.sidebar.button("📚  Courses & Marks", use_container_width=True):
        st.session_state.current_page = "Courses & Marks"
        st.rerun()

    if st.sidebar.button("📂  Assignments", use_container_width=True):
        st.session_state.current_page = "Assignments"
        st.rerun()

    if st.sidebar.button("🗓️  Timetable", use_container_width=True):
        st.session_state.current_page = "Timetable"
        st.rerun()

    if st.sidebar.button("💳  Fees & Accounts", use_container_width=True):
        st.session_state.current_page = "Fees"
        st.rerun()

    if st.sidebar.button("⭐  Faculty Feedback", use_container_width=True):
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

    if st.sidebar.button("📅  My Attendance", use_container_width=True):
        st.session_state.current_page = "My Attendance"
        st.rerun()

    if st.sidebar.button("📂  Course Assignments", use_container_width=True):
        st.session_state.current_page = "Student Assignments"
        st.rerun()

    if st.sidebar.button("🗓️  Class Schedule", use_container_width=True):
        st.session_state.current_page = "Student Timetable"
        st.rerun()

    if st.sidebar.button("💳  Fee Invoices", use_container_width=True):
        st.session_state.current_page = "Student Fees"
        st.rerun()

    if st.sidebar.button("📝  Grades & Transcript", use_container_width=True):
        st.session_state.current_page = "My Marks"
        st.rerun()

    if st.sidebar.button("🛠️  Academic Toolkit (CGPA)", use_container_width=True):
        st.session_state.current_page = "Academic Tools"
        st.rerun()

    if st.sidebar.button("⭐  Course Rating", use_container_width=True):
        st.session_state.current_page = "Student Feedback"
        st.rerun()

    if st.sidebar.button("🔒  Security", use_container_width=True):
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
        # Header from Figma Reference
        st.markdown("""
        <div style="margin-bottom: 24px;">
            <h1 style="font-size: 26px; font-weight: 800; color: #0f172a; margin-bottom: 4px;">Welcome back, Admin</h1>
            <p style="color: #64748b; font-size: 14px; margin: 0;">Here is a snapshot of the Academic Atelier performance today.</p>
        </div>
        """, unsafe_allow_html=True)

        stats = get_dashboard_stats()
        students = get_all_students()

        # Figma 3-Card Stat Metrics Row
        c1, c2, c3 = st.columns(3)
        with c1:
            st.metric(label="TOTAL STUDENTS", value=f"{stats['total_students']:,}", delta="+4% this term")
        with c2:
            st.metric(label="ACTIVE DEPARTMENTS", value=stats["total_departments"], delta="Verified")
        with c3:
            st.metric(label="OVERALL PASS RATE", value=f"{stats['pass_percentage']:.1f}%", delta=f"{stats['average_marks']:.1f}% Avg Score")

        st.write("")

        # Two Column Split from Figma: Recent Activities (Left) + Quick Actions & Alert (Right)
        col_left, col_right = st.columns([2, 1])

        with col_left:
            st.markdown("""
            <div class="figma-card">
                <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom: 14px;">
                    <h3 style="font-size: 16px; font-weight: 700; color: #0f172a; margin: 0;">Recent Activities</h3>
                    <span style="font-size: 13px; color: #2563eb; font-weight: 600; cursor: pointer;">Live Log</span>
                </div>
            """, unsafe_allow_html=True)

            # Sample dynamic activities from database
            notices = get_announcements()
            if students:
                latest_student = students[-1]
                st.markdown(f"""
                <div class="activity-row">
                    <div class="activity-icon" style="background-color: #eff6ff; color: #2563eb;">👤</div>
                    <div>
                        <div style="font-size: 14px; font-weight: 600; color: #1e293b;">New student registered</div>
                        <div style="font-size: 12px; color: #64748b;">{latest_student['name']} ({latest_student['roll_number']}) — {latest_student['department']} department</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

            st.markdown("""
                <div class="activity-row">
                    <div class="activity-icon" style="background-color: #fef3c7; color: #d97706;">📅</div>
                    <div>
                        <div style="font-size: 14px; font-weight: 600; color: #1e293b;">Attendance records synchronized</div>
                        <div style="font-size: 12px; color: #64748b;">Daily attendance verified across active engineering cohorts</div>
                    </div>
                </div>
            """, unsafe_allow_html=True)

            if notices:
                st.markdown(f"""
                <div class="activity-row">
                    <div class="activity-icon" style="background-color: #f3e8ff; color: #9333ea;">📢</div>
                    <div>
                        <div style="font-size: 14px; font-weight: 600; color: #1e293b;">{notices[0][0]}</div>
                        <div style="font-size: 12px; color: #64748b;">{notices[0][1][:65]}...</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

            st.markdown("</div>", unsafe_allow_html=True)

            # Institutional Early Warning Table
            st.markdown("""
            <div class="figma-card">
                <h3 style="font-size: 16px; font-weight: 700; color: #0f172a; margin: 0 0 12px 0;">Academic Intervention Roster</h3>
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
                    st.success("✅ All enrolled students are meeting minimum passing criteria.")
            else:
                st.info("Performance stats will calculate automatically when marks are entered.")
            st.markdown("</div>", unsafe_allow_html=True)

        with col_right:
            st.markdown("""
            <div class="figma-card">
                <h3 style="font-size: 16px; font-weight: 700; color: #0f172a; margin: 0 0 14px 0;">Quick Actions</h3>
            """, unsafe_allow_html=True)

            if st.button("➕ Add Student", key="qa_add_st", use_container_width=True):
                st.session_state.current_page = "Students"
                st.rerun()

            if st.button("📅 Mark Attendance", key="qa_att", use_container_width=True):
                st.session_state.current_page = "Attendance"
                st.rerun()

            if st.button("📂 Create Assignment", key="qa_assign", use_container_width=True):
                st.session_state.current_page = "Assignments"
                st.rerun()

            st.markdown("""
                <div class="action-required-card">
                    <div class="action-required-title">! Action Required</div>
                    <div class="action-required-desc">
                        End-of-term attendance reviews require validation. Flagged students with &lt; 75% attendance will require hall ticket clearance.
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)

        # Figma Big Bottom Blue Banner Card
        st.markdown("""
        <div class="institutional-banner">
            <h2 style="font-size: 22px; font-weight: 800; margin: 0 0 8px 0; color: #ffffff;">Upgrading the Digital Infrastructure for 2026</h2>
            <p style="color: #e0f2fe; font-size: 14px; max-width: 650px; line-height: 1.5; margin-bottom: 20px;">
                Our campus migration to centralized student-faculty portals and live attendance sync is currently active.
            </p>
            <span style="background-color: #ffffff; color: #1e3a8a; font-weight: 700; padding: 10px 20px; border-radius: 8px; font-size: 13px; display: inline-block;">
                Institutional Roadmap Active
            </span>
        </div>
        """, unsafe_allow_html=True)

    elif st.session_state.current_page == "Students":
        render_page(["Student_Management.py", "1_Student_Management.py", "3_Student_Management.py"])

    elif st.session_state.current_page == "Attendance":
        st.title("📅 Attendance Registry")
        st.markdown("<p style='color: #64748b;'>Record daily student attendance by department and subject.</p>", unsafe_allow_html=True)

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
            <h1 style="font-size: 26px; font-weight: 800; color: #0f172a; margin-bottom: 4px;">Welcome back, {student.get('name', 'Student')}</h1>
            <p style="color: #64748b; font-size: 14px; margin: 0;">Academic Atelier Enrolled Candidate Dashboard</p>
        </div>
        """, unsafe_allow_html=True)

        col1, col2 = st.columns([1, 2])
        with col1:
            st.markdown(f"""
            <div class="figma-card">
                <h3 style="margin-top:0; color: #0f172a;">{student.get('name')}</h3>
                <p style="color: #2563eb; font-weight: 700; font-size: 15px; margin-bottom: 12px;">Roll: {student.get('roll_number')}</p>
                <hr style="border: 0.5px solid #e2e8f0; margin: 12px 0;">
                <p style="font-size:14px; margin:6px 0;"><strong>Department:</strong> {student.get('department')}</p>
                <p style="font-size:14px; margin:6px 0;"><strong>Academic Year:</strong> Year {student.get('year')}</p>
                <p style="font-size:14px; margin:6px 0;"><strong>Email:</strong> {student.get('email')}</p>
                <p style="font-size:14px; margin:6px 0;"><strong>Status:</strong> <span style="color:#16a34a; font-weight:600;">Active Enrolled</span></p>
            </div>
            """, unsafe_allow_html=True)

            with st.expander("🪪 View Exam Admit Card"):
                st.markdown(f"""
                <div style="background: #ffffff; border: 2px solid #2563eb; border-radius: 12px; padding: 18px; box-shadow: 0 4px 12px rgba(37,99,235,0.1);">
                    <div style="text-align: center; border-bottom: 1px solid #e2e8f0; padding-bottom: 8px;">
                        <h4 style="color: #1e3a8a; margin: 0;">ACADEMIC ATELIER</h4>
                        <p style="color: #64748b; font-size: 11px; margin: 0;">SEMESTER ADMIT CARD</p>
                    </div>
                    <div style="display: flex; justify-content: space-between; margin-top: 14px; font-size: 13px;">
                        <div>
                            <p style="margin:4px 0;"><strong>Name:</strong> {student.get('name')}</p>
                            <p style="margin:4px 0;"><strong>Roll:</strong> {student.get('roll_number')}</p>
                            <p style="margin:4px 0;"><strong>Dept:</strong> {student.get('department')}</p>
                            <p style="margin:4px 0;"><strong>Year:</strong> Year {student.get('year')}</p>
                        </div>
                        <div style="border: 1px dashed #cbd5e1; width: 80px; height: 100px; display:flex; align-items:center; justify-content:center; border-radius: 6px;">
                            <span style="font-size: 10px; color:#94a3b8;">Photo</span>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

        with col2:
            st.markdown("""
            <div class="figma-card">
                <h3 style="font-size: 16px; font-weight: 700; color: #0f172a; margin: 0 0 12px 0;">Institutional Bulletins</h3>
            """, unsafe_allow_html=True)
            notices = get_announcements()
            if notices:
                for title, msg, dt in notices:
                    st.markdown(f"""
                    <div style="border-bottom: 1px solid #f1f5f9; padding: 10px 0;">
                        <div style="display:flex; justify-content:space-between;">
                            <strong style="color:#0f172a;">{title}</strong>
                            <span style="font-size:12px; color:#94a3b8;">{dt}</span>
                        </div>
                        <p style="font-size:13px; color:#475569; margin: 4px 0 0 0;">{msg}</p>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.info("No active notices.")
            st.markdown("</div>", unsafe_allow_html=True)

    elif st.session_state.current_page == "My Attendance":
        st.title("📅 My Attendance")
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
                        if st.form_submit_button("Submit"):
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
        st.title("💳 Fee Invoices")
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
