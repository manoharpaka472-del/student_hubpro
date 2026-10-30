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
    get_announcements
)
from auth import require_login, logout_button

# ==========================================
# PAGE CONFIGURATION
# ==========================================
st.set_page_config(
    page_title="StudentHub Pro | Academic Suite",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Prevent duplicate logout render
st.session_state["_logout_rendered"] = False

# ==========================================
# 3D ANIMATED BACKGROUND & BUTTONS CSS
# ==========================================
st.markdown("""
<style>
    /* 3D Animated Mesh Gradient Background */
    @keyframes gradientShift {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }

    .stApp {
        background: linear-gradient(-45deg, #070a13, #0f172a, #0c1c38, #050b14);
        background-size: 400% 400%;
        animation: gradientShift 16s ease infinite;
        color: #f1f5f9;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    }

    /* Radial grid overlay */
    .stApp::before {
        content: "";
        position: fixed;
        top: 0; left: 0; width: 100%; height: 100%;
        background-image: 
            linear-gradient(rgba(255, 255, 255, 0.02) 1px, transparent 1px),
            linear-gradient(90deg, rgba(255, 255, 255, 0.02) 1px, transparent 1px);
        background-size: 32px 32px;
        pointer-events: none;
        z-index: 0;
    }

    /* Sidebar Glassmorphism */
    [data-testid="stSidebar"] {
        background-color: rgba(15, 23, 42, 0.88) !important;
        backdrop-filter: blur(14px) !important;
        border-right: 1px solid rgba(255, 255, 255, 0.08) !important;
    }

    /* 3D Tactile Animated Buttons */
    .stButton>button {
        width: 100%;
        background: linear-gradient(145deg, #1e293b, #0f172a) !important;
        color: #f8fafc !important;
        font-weight: 600 !important;
        border: 1px solid rgba(255, 255, 255, 0.12) !important;
        border-radius: 12px !important;
        padding: 12px 18px !important;
        margin-bottom: 8px !important;
        box-shadow: 0 6px 12px -2px rgba(0, 0, 0, 0.5), inset 0 1px 0 rgba(255, 255, 255, 0.15) !important;
        transition: all 0.22s cubic-bezier(0.4, 0, 0.2, 1) !important;
        transform: perspective(600px) translateZ(0);
    }
    .stButton>button:hover {
        background: linear-gradient(145deg, #2563eb, #1d4ed8) !important;
        color: #ffffff !important;
        transform: perspective(600px) translateY(-3px) translateZ(6px);
        box-shadow: 0 12px 24px -4px rgba(37, 99, 235, 0.55), inset 0 1px 0 rgba(255, 255, 255, 0.3) !important;
        border-color: rgba(147, 197, 253, 0.5) !important;
    }
    .stButton>button:active {
        transform: perspective(600px) translateY(2px) translateZ(-4px);
        box-shadow: 0 2px 6px rgba(0, 0, 0, 0.6) !important;
    }

    /* 3D Floating Stat Metric Cards */
    div[data-testid="stMetric"] {
        background: linear-gradient(135deg, rgba(30, 41, 59, 0.75), rgba(15, 23, 42, 0.95)) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        padding: 20px 22px !important;
        border-radius: 16px !important;
        box-shadow: 0 12px 28px -6px rgba(0, 0, 0, 0.6) !important;
        backdrop-filter: blur(10px);
        transition: transform 0.25s ease, border-color 0.25s ease, box-shadow 0.25s ease;
    }
    div[data-testid="stMetric"]:hover {
        transform: translateY(-5px);
        border-color: rgba(56, 189, 248, 0.5) !important;
        box-shadow: 0 16px 32px -4px rgba(56, 189, 248, 0.2) !important;
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
    }

    /* Role Badges */
    .role-badge {
        display: inline-block;
        padding: 5px 14px;
        border-radius: 20px;
        font-size: 11px;
        font-weight: 700;
        letter-spacing: 0.5px;
        margin-bottom: 8px;
    }
    .admin-badge {
        background: rgba(37, 99, 235, 0.18);
        color: #60a5fa;
        border: 1px solid rgba(59, 130, 246, 0.4);
    }
    .student-badge {
        background: rgba(16, 185, 129, 0.18);
        color: #34d399;
        border: 1px solid rgba(16, 185, 129, 0.4);
    }

    /* Glass Panels */
    .glass-card {
        background: rgba(30, 41, 59, 0.7);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 14px;
        padding: 22px;
        backdrop-filter: blur(8px);
        box-shadow: 0 10px 20px rgba(0,0,0,0.3);
    }
</style>
""", unsafe_allow_html=True)

# Authentication enforcement
require_login()

user_role = st.session_state.get("role", "admin")

# Initialize default page based on role
if "current_page" not in st.session_state:
    st.session_state.current_page = "Dashboard Overview" if user_role == "admin" else "My Academic Profile"


# ==========================================
# SIDEBAR NAVIGATION
# ==========================================
logout_button()

st.sidebar.markdown("""
<div style="padding: 10px 0 10px 0;">
    <h2 style="color: #f8fafc; font-size: 22px; margin: 0; font-weight: 800;">StudentHub<span style="color: #38bdf8;">.Pro</span></h2>
</div>
""", unsafe_allow_html=True)

if user_role == "admin":
    st.sidebar.markdown('<span class="role-badge admin-badge">ADMINISTRATOR</span>', unsafe_allow_html=True)
    st.sidebar.caption("System Management Suite")
    st.sidebar.markdown("### 📌 Navigation")

    if st.sidebar.button("📊  Executive Dashboard", use_container_width=True):
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

    if st.sidebar.button("📢  Campus Announcements", use_container_width=True):
        st.session_state.current_page = "Admin Announcements"
        st.rerun()

else:
    student = st.session_state.get("student_info", {})
    st.sidebar.markdown('<span class="role-badge student-badge">STUDENT PORTAL</span>', unsafe_allow_html=True)
    st.sidebar.markdown(f"**{student.get('name', 'Student')}**")
    st.sidebar.caption(f"Roll: `{student.get('roll_number', '')}`")
    st.sidebar.markdown("### 📌 Student Menu")

    if st.sidebar.button("🎓  My Academic Profile", use_container_width=True):
        st.session_state.current_page = "My Academic Profile"
        st.rerun()

    if st.sidebar.button("📝  My Marks & Grade Sheet", use_container_width=True):
        st.session_state.current_page = "My Marks"
        st.rerun()

    if st.sidebar.button("🛠️  Academic Toolkit (SGPA & Bunk)", use_container_width=True):
        st.session_state.current_page = "Academic Tools"
        st.rerun()

    if st.sidebar.button("🔒  Account & Security", use_container_width=True):
        st.session_state.current_page = "Account Security"
        st.rerun()

st.sidebar.divider()
st.sidebar.caption("StudentHub Enterprise Suite v3.0")


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
# ADMIN PAGE ROUTING
# ==========================================
if user_role == "admin":
    if st.session_state.current_page == "Dashboard Overview":
        st.markdown('<span class="role-badge admin-badge">INSTITUTIONAL METRICS</span>', unsafe_allow_html=True)
        st.title("🎓 Executive Campus Dashboard")
        st.markdown("<p style='color: #94a3b8; font-size: 15px;'>Real-time metrics, academic distribution, and performance alerts.</p>", unsafe_allow_html=True)

        stats = get_dashboard_stats()
        students = get_all_students()

        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Enrolled Students", f"{stats['total_students']:,}")
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
                fig_dep = px.bar(dep_counts, x="department", y="Students", color="department", title="Department Headcount", template="plotly_dark")
                fig_dep.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", showlegend=False)
                st.plotly_chart(fig_dep, use_container_width=True)

            with r_col:
                yr_counts = df.groupby("year").size().reset_index(name="Students")
                fig_yr = px.bar(yr_counts, x="year", y="Students", title="Enrollment by Academic Year", template="plotly_dark", color_discrete_sequence=["#38bdf8"])
                fig_yr.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", xaxis=dict(tickmode="linear", dtick=1))
                st.plotly_chart(fig_yr, use_container_width=True)

        st.divider()

        # Admin Tool 1: At-Risk Academic Warning System
        st.subheader("🚨 Academic Early Warning System (At-Risk Alerts)")
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
                st.warning(f"⚠️ {len(at_risk)} student(s) identified needing academic intervention:")
                st.dataframe(
                    at_risk.rename(columns={
                        "roll_number": "Roll No", "name": "Full Name",
                        "department": "Department", "avg_marks": "Average Score",
                        "failed_subjects": "Backlogs/Failed"
                    }).round({"Average Score": 2}),
                    use_container_width=True,
                    hide_index=True
                )
            else:
                st.success("✅ All enrolled students are currently in good academic standing (Pass Rate 100%).")
        else:
            st.info("Performance risk analytics will appear when marks are uploaded.")

        st.divider()

        # Admin Tool 2: Quick Roster Search & CSV Export
        st.subheader("🔍 Institutional Student Directory")
        if students:
            df_st = pd.DataFrame(students)
            query = st.text_input("Filter student directory by Name, Roll Number, or Department:", "")
            if query:
                df_st = df_st[
                    df_st["name"].str.contains(query, case=False, na=False) |
                    df_st["roll_number"].str.contains(query, case=False, na=False) |
                    df_st["department"].str.contains(query, case=False, na=False)
                ]

            st.dataframe(
                df_st[["roll_number", "name", "email", "department", "year"]].rename(
                    columns={"roll_number": "Roll No", "name": "Name", "email": "Email", "department": "Department", "year": "Year"}
                ),
                use_container_width=True,
                hide_index=True
            )

            csv = df_st.to_csv(index=False).encode("utf-8")
            st.download_button("📥 Export Directory to CSV", csv, "student_roster.csv", "text/csv")

    elif st.session_state.current_page == "Admin Announcements":
        st.markdown('<span class="role-badge admin-badge">BROADCAST</span>', unsafe_allow_html=True)
        st.title("📢 Campus Announcement Center")
        st.write("Post notices directly to the student portal dashboard.")

        with st.form("new_notice_form"):
            n_title = st.text_input("Notice Title", placeholder="e.g. Mid-Term Examination Schedule Released")
            n_msg = st.text_area("Notice Message / Details", placeholder="Enter the official announcement text...")
            post_btn = st.form_submit_button("Broadcast Notice", use_container_width=True)
            if post_btn:
                if n_title and n_msg:
                    add_announcement(n_title, n_msg)
                    st.success("Announcement successfully broadcast to student portal!")
                else:
                    st.warning("Please fill out both title and message.")

        st.subheader("Active Announcements")
        notices = get_announcements()
        if notices:
            for title, msg, dt in notices:
                st.markdown(f"""
                <div class="glass-card" style="margin-bottom: 12px;">
                    <div style="display:flex; justify-content:space-between;">
                        <h4 style="margin:0; color:#38bdf8;">{title}</h4>
                        <span style="font-size:12px; color:#64748b;">{dt}</span>
                    </div>
                    <p style="margin-top:8px; color:#cbd5e1;">{msg}</p>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("No notices currently posted.")

    elif st.session_state.current_page == "Student Management":
        render_page(["Student_Management.py", "1_Student_Management.py", "3_Student_Management.py"])

    elif st.session_state.current_page == "Course Management":
        render_page(["Course_Management.py", "1_Course_Management.py", "2_Course_Management.py"])

    elif st.session_state.current_page == "Marks Management":
        render_page(["Marks_Management.py", "2_Marks_Management.py", "3_Marks_Management.py"])


# ==========================================
# STUDENT PAGE ROUTING
# ==========================================
else:
    student = st.session_state.get("student_info", {})
    student_id = student.get("id")

    # Fetch marks for logged-in student
    with get_connection() as conn:
        marks_df = pd.read_sql_query(
            "SELECT subject, marks FROM marks WHERE student_id = ? ORDER BY subject",
            conn,
            params=(student_id,)
        )

    # 1. ACADEMIC PROFILE & CAMPUS NOTICES
    if st.session_state.current_page == "My Academic Profile":
        st.markdown('<span class="role-badge student-badge">VERIFIED PROFILE</span>', unsafe_allow_html=True)
        st.title(f"Welcome back, {student.get('name', 'Student')}!")
        st.write("")

        col1, col2 = st.columns([1, 2])
        with col1:
            st.markdown(f"""
            <div class="glass-card">
                <h3 style="margin-top:0; color: #f8fafc;">{student.get('name')}</h3>
                <p style="color: #38bdf8; font-weight: 700; font-size: 16px; margin: 0 0 10px 0;">Roll No: {student.get('roll_number')}</p>
                <hr style="border: 0.5px solid rgba(255,255,255,0.1); margin: 12px 0;">
                <p><strong>Department:</strong> {student.get('department')}</p>
                <p><strong>Academic Year:</strong> Year {student.get('year')}</p>
                <p><strong>Official Email:</strong> {student.get('email')}</p>
                <p><strong>Status:</strong> <span style="color:#34d399; font-weight:600;">Enrolled & Active</span></p>
            </div>
            """, unsafe_allow_html=True)

        with col2:
            st.subheader("📢 Campus Bulletin Board")
            notices = get_announcements()
            if notices:
                for title, msg, dt in notices:
                    st.markdown(f"""
                    <div class="glass-card" style="margin-bottom: 12px;">
                        <div style="display:flex; justify-content:space-between;">
                            <h4 style="margin:0; color:#38bdf8;">📌 {title}</h4>
                            <span style="font-size:12px; color:#64748b;">{dt}</span>
                        </div>
                        <p style="margin-top:6px; color:#cbd5e1; font-size:14px;">{msg}</p>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.info("No active announcements from administration.")

        st.divider()
        st.subheader("📊 Quick Academic Overview")
        if not marks_df.empty:
            avg_score = marks_df["marks"].mean()
            passed = len(marks_df[marks_df["marks"] >= 40])
            total = len(marks_df)

            m1, m2, m3 = st.columns(3)
            m1.metric("Cumulative Average", f"{avg_score:.2f}%")
            m2.metric("Courses Enrolled", total)
            m3.metric("Clearance Rate", f"{passed}/{total} Passed")

            fig = px.bar(
                marks_df, x="subject", y="marks",
                title="Course Score Breakdown",
                template="plotly_dark",
                color="marks",
                color_continuous_scale="Blues"
            )
            fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", yaxis_range=[0, 100])
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Marks records will appear once evaluated.")

    # 2. MARKS & OFFICIAL TRANSCRIPT
    elif st.session_state.current_page == "My Marks":
        st.markdown('<span class="role-badge student-badge">EXAM RESULTS</span>', unsafe_allow_html=True)
        st.title("📝 Official Semester Transcript")

        if not marks_df.empty:
            marks_df["Grade"] = marks_df["marks"].apply(
                lambda x: "O (Outstanding)" if x >= 90 else (
                    "A+ (Excellent)" if x >= 80 else (
                        "A (Very Good)" if x >= 70 else (
                            "B+ (Good)" if x >= 60 else (
                                "B (Above Average)" if x >= 50 else (
                                    "C (Pass)" if x >= 40 else "F (Fail)"
                                )
                            )
                        )
                    )
                )
            )

            st.dataframe(
                marks_df.rename(columns={"subject": "Subject Name", "marks": "Marks (Out of 100)"}),
                use_container_width=True,
                hide_index=True
            )

            # Official Text Transcript Generator
            transcript_text = f"""
=====================================================
            OFFICIAL ACADEMIC TRANSCRIPT             
=====================================================
Student Name : {student.get('name')}
Roll Number  : {student.get('roll_number')}
Department   : {student.get('department')}
Year         : {student.get('year')}
-----------------------------------------------------
Subject                      Marks    Grade
-----------------------------------------------------
"""
            for _, row in marks_df.iterrows():
                transcript_text += f"{row['subject']:<28} {row['marks']:<8} {row['Grade']}\n"
            transcript_text += f"-----------------------------------------------------\nCumulative Average: {marks_df['marks'].mean():.2f}%\n====================================================="

            col_d1, col_d2 = st.columns(2)
            with col_d1:
                st.download_button(
                    "📥 Download Grade Report (CSV)",
                    marks_df.to_csv(index=False).encode("utf-8"),
                    f"{student.get('roll_number')}_marks.csv",
                    "text/csv"
                )
            with col_d2:
                st.download_button(
                    "📄 Download Formal Transcript (.txt)",
                    transcript_text.encode("utf-8"),
                    f"{student.get('roll_number')}_transcript.txt",
                    "text/plain"
                )
        else:
            st.info("No exam records posted yet.")

    # 3. STUDENT SUCCESS TOOLKIT (SGPA & BUNK BUFFER)
    elif st.session_state.current_page == "Academic Tools":
        st.markdown('<span class="role-badge student-badge">STUDENT CALCULATORS</span>', unsafe_allow_html=True)
        st.title("🛠️ Academic Planning Toolkit")

        tab_calc1, tab_calc2 = st.tabs(["🎯 Target SGPA / Score Estimator", "📅 Attendance & Bunk Margin Planner"])

        with tab_calc1:
            st.markdown("#### Estimate Required Final Exam Marks")
            curr_pct = st.number_input("Current Midterm / Internal Score (%)", 0.0, 100.0, 65.0, 0.5)
            target = st.number_input("Target Goal (%)", 0.0, 100.0, 75.0, 0.5)
            weight = st.slider("Internal Assessment Weightage (%)", 10, 90, 40)

            rem_w = 100 - weight
            req = (target - (curr_pct * (weight / 100))) / (rem_w / 100)
            if req <= 100:
                st.success(f"You must score **{req:.1f}%** on the remaining semester exams to secure your {target:.1f}% goal!")
            else:
                st.error(f"Mathematically impossible: requires {req:.1f}% on remaining components.")

        with tab_calc2:
            st.markdown("#### Attendance Safety & Bunk Buffer Calculator")
            total_cls = st.number_input("Total Scheduled Semester Classes", min_value=1, value=60)
            attended = st.number_input("Classes Attended So Far", min_value=0, max_value=int(total_cls), value=50)

            cur_att = (attended / total_cls) * 100
            st.metric("Current Attendance", f"{cur_att:.1f}%")

            if cur_att >= 75.0:
                # Calculate safe classes to miss
                bunks = int((attended - (0.75 * total_cls)) / 0.75)
                st.success(f"Safe zone! You can miss up to **{max(0, bunks)}** more classes while staying above the 75% exam threshold.")
            else:
                req_classes = int(((0.75 * total_cls) - attended) / 0.25)
                st.error(f"Deficit! You must attend the next **{max(1, req_classes)}** consecutive classes without missing any to restore eligibility.")

    # 4. ACCOUNT & PASSWORD MANAGEMENT
    elif st.session_state.current_page == "Account Security":
        st.markdown('<span class="role-badge student-badge">SECURITY</span>', unsafe_allow_html=True)
        st.title("🔒 Change Portal Password")

        with st.form("change_pwd_form"):
            old_p = st.text_input("Current Password", type="password")
            new_p = st.text_input("New Password", type="password")
            confirm_p = st.text_input("Confirm New Password", type="password")
            sub_pwd = st.form_submit_button("Update Password", use_container_width=True)

            if sub_pwd:
                current_stored = student.get("password") or "student123"
                if old_p != current_stored:
                    st.error("Current password does not match.")
                elif new_p != confirm_p:
                    st.error("New passwords do not match.")
                elif len(new_p) < 4:
                    st.warning("Password must be at least 4 characters long.")
                else:
                    update_student_password(student["id"], new_p)
                    student["password"] = new_p
                    st.session_state["student_info"] = student
                    st.success("Password updated successfully!")
