import streamlit as st
import pandas as pd
import plotly.express as px
import os

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
    page_title="StudentHub Pro | Academic Portal",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==========================================
# AUTHENTICATION
# ==========================================
require_login()

# Prevent duplicate logout button rendering across sub-page calls
st.session_state["_logout_rendered"] = False

# ==========================================
# PREMIUM DESIGN SYSTEM & ANIMATED CSS
# ==========================================
st.markdown("""
<style>
    /* Dark Blueprint & Modern Radial Grid Background */
    .stApp {
        background-color: #0b0f19;
        background-image: 
            radial-gradient(at 100% 0%, rgba(30, 58, 138, 0.25) 0px, transparent 50%),
            radial-gradient(at 0% 100%, rgba(15, 23, 42, 0.8) 0px, transparent 50%),
            linear-gradient(rgba(255, 255, 255, 0.02) 1px, transparent 1px),
            linear-gradient(90deg, rgba(255, 255, 255, 0.02) 1px, transparent 1px);
        background-size: 100% 100%, 100% 100%, 36px 36px, 36px 36px;
        color: #f1f5f9;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    }

    /* Sidebar Glassmorphic Treatment */
    [data-testid="stSidebar"] {
        background-color: rgba(15, 23, 42, 0.85) !important;
        backdrop-filter: blur(12px) !important;
        border-right: 1px solid rgba(255, 255, 255, 0.08) !important;
    }

    /* Glassmorphic Metric Cards */
    div[data-testid="stMetric"] {
        background: linear-gradient(135deg, rgba(30, 41, 59, 0.7), rgba(15, 23, 42, 0.9)) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        padding: 20px 22px !important;
        border-radius: 14px !important;
        box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.5) !important;
        backdrop-filter: blur(8px);
        transition: transform 0.25s ease, border-color 0.25s ease;
    }
    div[data-testid="stMetric"]:hover {
        transform: translateY(-4px);
        border-color: rgba(56, 189, 248, 0.4) !important;
    }
    div[data-testid="stMetricLabel"] p {
        color: #94a3b8 !important;
        font-size: 13px !important;
        font-weight: 600 !important;
        letter-spacing: 0.5px;
        text-transform: uppercase;
    }
    div[data-testid="stMetricValue"] div {
        color: #38bdf8 !important;
        font-size: 32px !important;
        font-weight: 800 !important;
    }

    /* 3D Animated Navigation Buttons */
    .stButton>button {
        width: 100%;
        background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
        color: #e2e8f0 !important;
        font-weight: 600 !important;
        border: 1px solid rgba(255, 255, 255, 0.12) !important;
        border-radius: 10px !important;
        padding: 10px 18px !important;
        margin-bottom: 8px !important;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.3), inset 0 1px 0 rgba(255, 255, 255, 0.1);
        transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1) !important;
        display: flex;
        align-items: center;
        justify-content: flex-start;
    }
    .stButton>button:hover {
        background: linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%) !important;
        color: #ffffff !important;
        transform: translateY(-2px);
        box-shadow: 0 8px 20px -4px rgba(37, 99, 235, 0.5) !important;
        border-color: rgba(147, 197, 253, 0.5) !important;
    }
    .stButton>button:active {
        transform: translateY(1px);
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.4) !important;
    }

    /* Modern Table Customization */
    [data-testid="stDataFrame"] {
        border-radius: 12px;
        border: 1px solid rgba(255, 255, 255, 0.08);
        overflow: hidden;
    }

    /* Section Headers */
    .portal-badge {
        display: inline-block;
        padding: 4px 12px;
        background: rgba(37, 99, 235, 0.15);
        color: #60a5fa;
        border: 1px solid rgba(59, 130, 246, 0.3);
        border-radius: 20px;
        font-size: 12px;
        font-weight: 600;
        letter-spacing: 0.5px;
        margin-bottom: 8px;
    }
</style>
""", unsafe_allow_html=True)


# Initialize Active Page state
if "current_page" not in st.session_state:
    st.session_state.current_page = "Dashboard Overview"


# ==========================================
# SIDEBAR NAVIGATION
# ==========================================
logout_button()

st.sidebar.markdown("""
<div style="padding: 10px 0 15px 0;">
    <h2 style="color: #f8fafc; font-size: 22px; margin: 0; font-weight: 800;">StudentHub<span style="color: #38bdf8;">.Pro</span></h2>
    <p style="color: #64748b; font-size: 12px; margin: 0;">Enterprise Campus Administration</p>
</div>
""", unsafe_allow_html=True)

st.sidebar.markdown('<span class="portal-badge">ADMIN ACCESS ACTIVE</span>', unsafe_allow_html=True)

st.sidebar.markdown("### 📌 Navigation")

if st.sidebar.button("📊  Dashboard Overview", use_container_width=True):
    st.session_state.current_page = "Dashboard Overview"
    st.rerun()

if st.sidebar.button("👨‍🎓  Student Management", use_container_width=True):
    st.session_state.current_page = "Student Management"
    st.rerun()

if st.sidebar.button("📚  Course Management", use_container_width=True):
    st.session_state.current_page = "Course Management"
    st.rerun()

if st.sidebar.button("📝  Marks Management", use_container_width=True):
    st.session_state.current_page = "Marks Management"
    st.rerun()

st.sidebar.divider()
st.sidebar.caption("System Version: 2.4.0-Production\nDatabase: SQLite3 Cloud Connector")


# ==========================================
# DYNAMIC PAGE RENDER ENGINE
# ==========================================
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
# PAGE ROUTING
# ==========================================

# 1. DASHBOARD OVERVIEW PAGE
if st.session_state.current_page == "Dashboard Overview":
    st.markdown('<span class="portal-badge">PORTAL OVERVIEW</span>', unsafe_allow_html=True)
    st.title("🎓 Executive Academic Dashboard")
    st.markdown("<p style='color: #94a3b8; font-size: 15px; margin-top: -8px;'>Real-time institutional performance metrics, cohort distribution, and student success tracking.</p>", unsafe_allow_html=True)
    st.write("")

    stats = get_dashboard_stats()
    students = get_all_students()

    # Stat Badges
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Enrolled", f"{stats['total_students']:,}")
    col2.metric("Departments", stats["total_departments"])
    col3.metric("Cohort Avg Marks", f"{stats['average_marks']:.2f}%")
    col4.metric("Subject Pass Rate", f"{stats['pass_percentage']:.1f}%")

    st.write("")
    st.write("")

    # Visual Analytics
    st.subheader("📈 Cohort & Enrollment Analytics")
    if students:
        df = pd.DataFrame(students)
        left_col, right_col = st.columns(2)
        
        with left_col:
            dep_counts = df.groupby("department").size().reset_index(name="Students")
            fig_dep = px.bar(
                dep_counts,
                x="department",
                y="Students",
                color="department",
                title="Student Distribution by Department",
                template="plotly_dark"
            )
            fig_dep.update_layout(
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                showlegend=False,
                margin=dict(l=20, r=20, t=40, b=20)
            )
            st.plotly_chart(fig_dep, use_container_width=True)

        with right_col:
            year_counts = df.groupby("year").size().reset_index(name="Students")
            fig_yr = px.bar(
                year_counts,
                x="year",
                y="Students",
                title="Student Distribution by Academic Year",
                template="plotly_dark",
                color_discrete_sequence=["#38bdf8"]
            )
            fig_yr.update_layout(
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                xaxis=dict(tickmode="linear", dtick=1),
                margin=dict(l=20, r=20, t=40, b=20)
            )
            st.plotly_chart(fig_yr, use_container_width=True)
    else:
        st.info("Enrollment distributions will populate once students are added.")

    st.divider()

    # Student Utility Tools (SGPA & Attendance Estimators)
    st.subheader("🛠️ Student Success Toolkit")
    tool_col1, tool_col2 = st.columns(2)

    with tool_col1:
        with st.expander("🎯 Target SGPA / Percentage Planner", expanded=False):
            st.write("Calculate what score you need on your remaining exams:")
            current_pct = st.number_input("Current Average (%)", min_value=0.0, max_value=100.0, value=65.0, step=0.5)
            target_pct = st.number_input("Target Goal (%)", min_value=0.0, max_value=100.0, value=75.0, step=0.5)
            completed_wt = st.slider("Completed Semester Weightage (%)", 10, 90, 50)

            rem_wt = 100 - completed_wt
            req_score = (target_pct - (current_pct * (completed_wt / 100))) / (rem_wt / 100)
            if req_score <= 100:
                st.success(f"You need an average of **{req_score:.1f}%** across remaining assessments to hit your target.")
            else:
                st.warning(f"Mathematically impossible: requires {req_score:.1f}% on remaining components.")

    with tool_col2:
        with st.expander("📅 75% Mandatory Attendance Safety Check", expanded=False):
            st.write("Ensure semester exam clearance compliance:")
            total_classes = st.number_input("Total Scheduled Classes", min_value=1, value=60)
            attended_classes = st.number_input("Classes Attended", min_value=0, max_value=int(total_classes), value=48)

            att_pct = (attended_classes / total_classes) * 100
            if att_pct >= 75.0:
                st.success(f"Current Attendance: **{att_pct:.1f}%** (Exam Eligible ✅)")
            else:
                classes_needed = (0.75 * total_classes - attended_classes) / 0.25
                st.error(f"Current: **{att_pct:.1f}%** (Deficit: Attend next **{max(1, int(classes_needed))}** consecutive classes).")

    st.divider()

    # Quick Search & Data Export
    st.subheader("🔍 Student Record Explorer")
    if students:
        df_students = pd.DataFrame(students)
        search_query = st.text_input("Search student by Name, Roll Number, or Department:", "")
        
        if search_query:
            filtered_df = df_students[
                df_students["name"].str.contains(search_query, case=False, na=False) |
                df_students["roll_number"].str.contains(search_query, case=False, na=False) |
                df_students["department"].str.contains(search_query, case=False, na=False)
            ]
        else:
            filtered_df = df_students

        display_df = filtered_df[["roll_number", "name", "email", "department", "year"]].rename(
            columns={
                "roll_number": "Roll No.",
                "name": "Full Name",
                "email": "Official Email",
                "department": "Department",
                "year": "Current Year"
            }
        )

        st.dataframe(display_df, use_container_width=True, hide_index=True)

        # Download Export
        csv_data = display_df.to_csv(index=False).encode("utf-8")
        st.download_button(
            label="📥 Export Filtered Roster to CSV",
            data=csv_data,
            file_name="student_roster.csv",
            mime="text/csv",
        )
    else:
        st.info("No records present to display.")

# 2. STUDENT MANAGEMENT PAGE
elif st.session_state.current_page == "Student Management":
    render_page(["Student_Management.py", "1_Student_Management.py", "3_Student_Management.py"])

# 3. COURSE MANAGEMENT PAGE
elif st.session_state.current_page == "Course Management":
    render_page(["Course_Management.py", "1_Course_Management.py", "2_Course_Management.py"])

# 4. MARKS MANAGEMENT PAGE
elif st.session_state.current_page == "Marks Management":
    render_page(["Marks_Management.py", "2_Marks_Management.py", "3_Marks_Management.py"])
