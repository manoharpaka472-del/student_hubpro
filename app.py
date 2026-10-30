import streamlit as st
import pandas as pd
import plotly.express as px

from database import (
    get_all_students,
    get_dashboard_stats,
    get_connection
)
from auth import require_login, logout_button

# ==========================================
# PAGE CONFIGURATION
# ==========================================
st.set_page_config(
    page_title="StudentHub Pro",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==========================================
# AUTHENTICATION
# ==========================================
require_login()st.session_state["_logout_rendered"] = False

# ==========================================
# CUSTOM CSS (High Contrast Dashboard Cards)
# ==========================================
st.markdown("""
<style>
    div[data-testid="stMetric"] {
        background-color: #1e293b !important;
        border: 1px solid #334155 !important;
        padding: 18px !important;
        border-radius: 10px !important;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.2) !important;
    }
    div[data-testid="stMetricLabel"] p {
        color: #94a3b8 !important;
        font-size: 14px !important;
        font-weight: 600 !important;
    }
    div[data-testid="stMetricValue"] div {
        color: #f8fafc !important;
        font-size: 28px !important;
        font-weight: 700 !important;
    }
    .stButton>button {
        width: 100%;
        text-align: left;
        border-radius: 8px;
        padding: 10px 15px;
        margin-bottom: 5px;
    }
</style>
""", unsafe_allow_html=True)

# Initialize Active Page state
if "current_page" not in st.session_state:
    st.session_state.current_page = "Dashboard Overview"

# ==========================================
# SIDEBAR NAVIGATION (Real, Working Buttons)
# ==========================================
logout_button()
st.sidebar.title("🎓 StudentHub Pro")
st.sidebar.divider()
st.sidebar.success("Administrator authenticated")
st.sidebar.markdown("### 📌 Navigation")

if st.sidebar.button("📊 Dashboard Overview", use_container_width=True):
    st.session_state.current_page = "Dashboard Overview"
    st.rerun()

if st.sidebar.button("👨‍🎓 Student Management", use_container_width=True):
    st.session_state.current_page = "Student Management"
    st.rerun()

if st.sidebar.button("📚 Course Management", use_container_width=True):
    st.session_state.current_page = "Course Management"
    st.rerun()

if st.sidebar.button("📝 Marks Management", use_container_width=True):
    st.session_state.current_page = "Marks Management"
    st.rerun()

st.sidebar.divider()
st.sidebar.info("Manage student records and monitor academic performance from one dashboard.")

# ==========================================
# PAGE ROUTING LOGIC
# ==========================================
# ==========================================
# PAGE ROUTING HELPER & LOGIC
# ==========================================

import os

def render_page(filename_variations):
    current_dir = os.path.dirname(os.path.abspath(__file__))
    candidates = []
    
    # Check both root and pages/ folder for all filename variations
    for fname in filename_variations:
        candidates.append(os.path.join(current_dir, "pages", fname))
        candidates.append(os.path.join(current_dir, fname))
        candidates.append(os.path.join("pages", fname))
        candidates.append(fname)
        
    found_path = None
    for path in candidates:
        if os.path.exists(path):
            found_path = path
            break

    if found_path:
        with open(found_path, "r", encoding="utf-8") as f:
            code = f.read()
            # Execute the page script directly in the current context
            exec(code, globals())
    else:
        pages_folder = os.path.join(current_dir, "pages")
        available = os.listdir(pages_folder) if os.path.exists(pages_folder) else "pages directory not found"
        st.error(f"Could not locate file: {filename_variations[0]}. Available files in pages/: {available}")


# 1. DASHBOARD OVERVIEW PAGE
if st.session_state.current_page == "Dashboard Overview":
    st.title("🎓 StudentHub Pro")
    st.markdown("<p style='color: #94a3b8;'>Smart Student Management & Academic Analytics</p>", unsafe_allow_html=True)
    st.divider()

    stats = get_dashboard_stats()
    students = get_all_students()

    st.subheader("📊 Dashboard Overview")
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("👨‍🎓 Total Students", stats["total_students"])
    col2.metric("🏫 Departments", stats["total_departments"])
    col3.metric("📈 Average Marks", f"{stats['average_marks']:.2f}%")
    col4.metric("✅ Subject Pass Rate", f"{stats['pass_percentage']:.1f}%")

    st.divider()

    st.subheader("📈 Student Analytics")
    if students:
        df = pd.DataFrame(students)
        left_col, right_col = st.columns(2)
        with left_col:
            st.markdown("#### 🏫 Department-wise Students")
            dep_counts = df.groupby("department").size().reset_index(name="Students")
            dep_chart = px.bar(dep_counts, x="department", y="Students", color="department")
            dep_chart.update_layout(showlegend=False)
            st.plotly_chart(dep_chart, use_container_width=True)

        with right_col:
            st.markdown("#### 📚 Year-wise Students")
            yr_counts = df.groupby("year").size().reset_index(name="Students")
            yr_chart = px.bar(yr_counts, x="year", y="Students")
            st.plotly_chart(yr_chart, use_container_width=True)
    else:
        st.info("No student records are available yet.")

    st.divider()

    st.subheader("📝 Academic Performance")
    with get_connection() as conn:
        marks_df = pd.read_sql_query(
            """
            SELECT s.roll_number, s.name, s.department, m.subject, m.marks
            FROM marks m
            INNER JOIN students s ON s.id = m.student_id
            ORDER BY s.name
            """,
            conn
        )

    if not marks_df.empty:
        c1, c2 = st.columns(2)
        with c1:
            dep_perf = marks_df.groupby("department")["marks"].mean().reset_index()
            perf_chart = px.bar(dep_perf, x="department", y="marks", color="department")
            perf_chart.update_layout(showlegend=False, yaxis_range=[0, 100])
            st.plotly_chart(perf_chart, use_container_width=True)

        with c2:
            marks_chart = px.histogram(marks_df, x="marks", nbins=10)
            marks_chart.update_layout(xaxis_range=[0, 100])
            st.plotly_chart(marks_chart, use_container_width=True)
    else:
        st.info("Academic charts will appear after you enter marks.")

    st.divider()

    st.subheader("👨‍🎓 Recent Student Registrations")
    if students:
        recent = pd.DataFrame(students)[["roll_number", "name", "email", "department", "year"]].head(10)
        recent.columns = ["Roll Number", "Student Name", "Email", "Department", "Year"]
        st.dataframe(recent, use_container_width=True, hide_index=True)


# 2. STUDENT MANAGEMENT PAGE
elif st.session_state.current_page == "Student Management":
    render_page([
        "Student_Management.py",
        "1_Student_Management.py",
        "3_Student_Management.py"
    ])


# 3. COURSE MANAGEMENT PAGE
elif st.session_state.current_page == "Course Management":
    render_page([
        "Course_Management.py",
        "1_Course_Management.py",
        "2_Course_Management.py"
    ])


# 4. MARKS MANAGEMENT PAGE
elif st.session_state.current_page == "Marks Management":
    render_page([
        "Marks_Management.py",
        "2_Marks_Management.py",
        "3_Marks_Management.py"
    ])

