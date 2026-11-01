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
            exec(
