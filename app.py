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

# Prevent duplicate logout render
st.session_state["_logout_rendered"] = False

# ==========================================
# CUSTOM CSS & THEME
# ==========================================
st.markdown("""
<style>
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

    [data-testid="stSidebar"] {
        background-color: rgba(15, 23, 42, 0.85) !important;
        backdrop-filter: blur(12px) !important;
        border-right: 1px solid rgba(255, 255, 255, 0.08) !important;
    }

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

    .stButton>button {
        width: 100%;
        background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
        color: #e2e8f0 !important;
        font-weight: 600 !important;
        border: 1px solid rgba(255, 255, 255, 0.12) !important;
        border-radius: 10px !important;
        padding: 10px 18px !important;
        margin-bottom: 8px !important;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.3);
        transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1) !important;
    }
    .stButton>button:hover {
        background: linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%) !important;
        color: #ffffff !important;
        transform: translateY(-2px);
        box-shadow: 0 8px 20px -4px rgba(37, 99, 235, 0.5) !important;
    }
    .stButton>button:active {
        transform: translateY(1px);
    }

    .role-badge {
        display: inline-block;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 12px;
        font-weight: 600;
        letter-spacing: 0.5px;
        margin-bottom: 8px;
    }
    .admin-badge {
        background: rgba(37, 99, 235, 0.15);
        color: #60a5fa;
        border: 1px solid rgba(59, 130, 246, 0.3);
    }
    .student-badge {
        background: rgba(16, 185, 129, 0.15);
        color: #34d399;
        border: 1px solid rgba(16, 185, 129, 0.3);
    }
</style>
""", unsafe_allow_html=True)

# Authentication enforcement
require_login()

user_role = st.session_state.get("role", "admin")

# Initialize default page based on role
if "current_page" not in st.session_state:
    st.session_state.current_page = "Dashboard Overview" if user_role == "admin" else "My Student Portal"


# ==========================================
# SIDEBAR
# ==========================================
logout_button()

st.sidebar.markdown("""
<div style="padding: 10px 0 10px 0;">
    <h2 style="color: #f8fafc; font-size: 22px; margin: 0; font-weight: 800;">StudentHub<span style="color: #38bdf8;">.Pro</span></h2>
</div>
""", unsafe_allow_html=True)

if user_role == "admin":
    st.sidebar.markdown('<span class="role-badge admin-badge">ADMINISTRATOR</span>', unsafe_allow_html=True)
    st.sidebar.caption("Full Administrative Privileges")
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

else:
    student = st.session_state.get("student_info", {})
    st.sidebar.markdown('<span class="role-badge student-badge">STUDENT PORTAL</span>', unsafe_allow_html=True)
    st.sidebar.markdown(f"**{student.get('name', 'Student')}**")
    st.sidebar.caption(f"Roll No: `{student.get('roll_number', '')}`")
    st.sidebar.markdown("### 📌 Student Menu")

    if st.sidebar.button("🎓  My Academic Profile", use_container_width=True):
        st.session_state.current_page = "My Student Portal"
        st.rerun()

    if st.sidebar.button("📝  My Marks & Grade Sheet", use_container_width=True):
        st.session_state.current_page = "My Marks"
        st.rerun()

    if st.sidebar.button("🛠️  Academic Toolkit (SGPA & Attendance)", use_container_width=True):
        st.session_state.current_page = "Academic Tools"
        st.rerun()

st.sidebar.divider()
st.sidebar.info("StudentHub Pro Enterprise Academic Suite")


# ==========================================
# SUB-PAGE LOADER FOR ADMIN
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
# PAGE ROUTING: ADMIN VIEWS
# ==========================================
if user_role == "admin":
    if st.session_state.current_page == "Dashboard Overview":
        st.markdown('<span class="role-badge admin-badge">ADMIN DASHBOARD</span>', unsafe_allow_html=True)
        st.title("🎓 Institutional Overview")
        st.markdown("<p style='color: #94a3b8;'>Real-time metrics, cohort distribution, and academic performance.</p>", unsafe_allow_html=True)

        stats = get_dashboard_stats()
        students = get_all_students()

        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Total Enrolled", f"{stats['total_students']:,}")
        c2.metric("Departments", stats["total_departments"])
        c3.metric("Cohort Avg Marks", f"{stats['average_marks']:.2f}%")
        c4.metric("Subject Pass Rate", f"{stats['pass_percentage']:.1f}%")

        st.write("")
        st.subheader("📈 Cohort Analytics")
        if students:
            df = pd.DataFrame(students)
            l_col, r_col = st.columns(2)
            with l_col:
                dep_counts = df.groupby("department").size().reset_index(name="Students")
                fig_dep = px.bar(dep_counts, x="department", y="Students", color="department", title="By Department", template="plotly_dark")
                fig_dep.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", showlegend=False)
                st.plotly_chart(fig_dep, use_container_width=True)

            with r_col:
                yr_counts = df.groupby("year").size().reset_index(name="Students")
                fig_yr = px.bar(yr_counts, x="year", y="Students", title="By Academic Year", template="plotly_dark", color_discrete_sequence=["#38bdf8"])
                fig_yr.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", xaxis=dict(tickmode="linear", dtick=1))
                st.plotly_chart(fig_yr, use_container_width=True)

        st.divider()
        st.subheader("🔍 Quick Student Finder")
        if students:
            search_query = st.text_input("Filter roster by Roll No, Name, or Department:", "")
            df_st = pd.DataFrame(students)
            if search_query:
                df_st = df_st[
                    df_st["name"].str.contains(search_query, case=False, na=False) |
                    df_st["roll_number"].str.contains(search_query, case=False, na=False) |
                    df_st["department"].str.contains(search_query, case=False, na=False)
                ]
            st.dataframe(df_st[["roll_number", "name", "email", "department", "year"]].rename(
                columns={"roll_number": "Roll No.", "name": "Name", "email": "Email", "department": "Department", "year": "Year"}
            ), use_container_width=True, hide_index=True)

    elif st.session_state.current_page == "Student Management":
        render_page(["Student_Management.py", "1_Student_Management.py", "3_Student_Management.py"])

    elif st.session_state.current_page == "Course Management":
        render_page(["Course_Management.py", "1_Course_Management.py", "2_Course_Management.py"])

    elif st.session_state.current_page == "Marks Management":
        render_page(["Marks_Management.py", "2_Marks_Management.py", "3_Marks_Management.py"])


# ==========================================
# PAGE ROUTING: STUDENT VIEWS
# ==========================================
else:
    student = st.session_state.get("student_info", {})
    student_id = student.get("id")

    # Fetch this specific student's marks
    with get_connection() as conn:
        marks_df = pd.read_sql_query(
            "SELECT subject, marks FROM marks WHERE student_id = ? ORDER BY subject",
            conn,
            params=(student_id,)
        )

    # 1. PROFILE VIEW
    if st.session_state.current_page == "My Student Portal":
        st.markdown('<span class="role-badge student-badge">STUDENT RECORD</span>', unsafe_allow_html=True)
        st.title(f"Welcome back, {student.get('name', 'Student')}!")
        st.markdown("<p style='color: #94a3b8;'>Verified academic record card.</p>", unsafe_allow_html=True)
        st.write("")

        col1, col2 = st.columns([1, 2])
        with col1:
            st.markdown(f"""
            <div style="background: rgba(30, 41, 59, 0.8); border: 1px solid rgba(255, 255, 255, 0.1); border-radius: 12px; padding: 24px;">
                <h3 style="margin-top:0; color: #f8fafc;">{student.get('name')}</h3>
                <p style="color: #38bdf8; font-weight: 700; font-size: 16px;">Roll No: {student.get('roll_number')}</p>
                <hr style="border: 0.5px solid rgba(255,255,255,0.1);">
                <p><strong>Department:</strong> {student.get('department')}</p>
                <p><strong>Academic Year:</strong> Year {student.get('year')}</p>
                <p><strong>Registered Email:</strong> {student.get('email')}</p>
            </div>
            """, unsafe_allow_html=True)

        with col2:
            st.subheader("📊 Performance Summary")
            if not marks_df.empty:
                avg_score = marks_df["marks"].mean()
                total_subs = len(marks_df)
                passed_subs = len(marks_df[marks_df["marks"] >= 40])

                m1, m2, m3 = st.columns(3)
                m1.metric("Average Score", f"{avg_score:.2f}%")
                m2.metric("Enrolled Subjects", total_subs)
                m3.metric("Passed Subjects", f"{passed_subs}/{total_subs}")

                # Performance Chart
                fig = px.bar(
                    marks_df,
                    x="subject",
                    y="marks",
                    title="My Subject Scores",
                    template="plotly_dark",
                    color="marks",
                    color_continuous_scale="Blues"
                )
                fig.update_layout(
                    paper_bgcolor="rgba(0,0,0,0)",
                    plot_bgcolor="rgba(0,0,0,0)",
                    yaxis_range=[0, 100]
                )
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No exam marks have been posted for your account yet.")

    # 2. MARKS VIEW
    elif st.session_state.current_page == "My Marks":
        st.markdown('<span class="role-badge student-badge">EXAM RESULTS</span>', unsafe_allow_html=True)
        st.title("📝 Grade Report Sheet")

        if not marks_df.empty:
            marks_df["Status"] = marks_df["marks"].apply(lambda x: "PASS ✅" if x >= 40 else "FAIL ❌")
            st.dataframe(
                marks_df.rename(columns={"subject": "Subject Name", "marks": "Marks Obtained"}),
                use_container_width=True,
                hide_index=True
            )

            csv = marks_df.to_csv(index=False).encode("utf-8")
            st.download_button(
                label="📥 Download Official Grade Report (CSV)",
                data=csv,
                file_name=f"{student.get('roll_number')}_marks.csv",
                mime="text/csv"
            )
        else:
            st.info("No marks records found.")

    # 3. TOOLS VIEW
    elif st.session_state.current_page == "Academic Tools":
        st.markdown('<span class="role-badge student-badge">STUDENT TOOLS</span>', unsafe_allow_html=True)
        st.title("🛠️ Academic Calculators")

        c1, c2 = st.columns(2)
        with c1:
            st.subheader("🎯 Target SGPA / Percentage Planner")
            current_pct = st.number_input("Current Average (%)", min_value=0.0, max_value=100.0, value=65.0, step=0.5)
            target_pct = st.number_input("Target Goal (%)", min_value=0.0, max_value=100.0, value=75.0, step=0.5)
            completed_wt = st.slider("Completed Semester Weightage (%)", 10, 90, 50)

            rem_wt = 100 - completed_wt
            req_score = (target_pct - (current_pct * (completed_wt / 100))) / (rem_wt / 100)
            if req_score <= 100:
                st.success(f"You need an average of **{req_score:.1f}%** across remaining assessments.")
            else:
                st.warning(f"Requires {req_score:.1f}% on remaining components.")

        with c2:
            st.subheader("📅 75% Mandatory Attendance Safety Check")
            total_classes = st.number_input("Total Scheduled Classes", min_value=1, value=60)
            attended_classes = st.number_input("Classes Attended", min_value=0, max_value=int(total_classes), value=48)

            att_pct = (attended_classes / total_classes) * 100
            if att_pct >= 75.0:
                st.success(f"Current Attendance: **{att_pct:.1f}%** (Exam Eligible ✅)")
            else:
                classes_needed = (0.75 * total_classes - attended_classes) / 0.25
                st.error(f"Current: **{att_pct:.1f}%** (Attend next **{max(1, int(classes_needed))}** consecutive classes).")
