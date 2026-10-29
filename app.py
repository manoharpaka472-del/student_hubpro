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

require_login()


# ==========================================
# CUSTOM CSS (Fix Invisible Metric Text & Cards)
# ==========================================

st.markdown("""
<style>
    /* Metric container styling */
    div[data-testid="stMetric"] {
        background-color: #1e293b !important;
        border: 1px solid #334155 !important;
        padding: 18px !important;
        border-radius: 10px !important;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.2) !important;
    }
    
    /* Metric labels (Titles) */
    div[data-testid="stMetricLabel"] p {
        color: #94a3b8 !important;
        font-size: 14px !important;
        font-weight: 600 !important;
    }
    
    /* Metric values (Numbers/Stats) */
    div[data-testid="stMetricValue"] div {
        color: #ffffff !important;
        font-size: 28px !important;
        font-weight: 700 !important;
    }

    .dashboard-subtitle {
        color: #94a3b8;
        font-size: 16px;
        margin-top: -10px;
        margin-bottom: 20px;
    }

    .dashboard-footer {
        text-align: center;
        color: #64748b;
        font-size: 13px;
        margin-top: 50px;
        padding-top: 20px;
        border-top: 1px solid #334155;
    }
</style>
""", unsafe_allow_html=True)


# ==========================================
# SIDEBAR
# ==========================================

logout_button()

st.sidebar.divider()
st.sidebar.success("Administrator authenticated")
st.sidebar.divider()

st.sidebar.info(
    "Manage student records and monitor academic performance from one dashboard."
)


# ==========================================
# DASHBOARD HEADER
# ==========================================

st.title("🎓 StudentHub Pro")

st.markdown(
    """
    <p class="dashboard-subtitle">
        Smart Student Management & Academic Analytics
    </p>
    """,
    unsafe_allow_html=True
)

st.divider()


# ==========================================
# LOAD DATABASE STATISTICS
# ==========================================

stats = get_dashboard_stats()
students = get_all_students()


# ==========================================
# DASHBOARD METRICS (Now fully visible)
# ==========================================

st.subheader("📊 Dashboard Overview")

col1, col2, col3, col4 = st.columns(4)

col1.metric(
    label="👨‍🎓 Total Students",
    value=stats["total_students"]
)

col2.metric(
    label="🏫 Departments",
    value=stats["total_departments"]
)

col3.metric(
    label="📈 Average Marks",
    value=f"{stats['average_marks']:.2f}%"
)

col4.metric(
    label="✅ Subject Pass Rate",
    value=f"{stats['pass_percentage']:.1f}%"
)

st.divider()


# ==========================================
# STUDENT DISTRIBUTION CHARTS
# ==========================================

st.subheader("📈 Student Analytics")

if students:
    df = pd.DataFrame(students)
    left_col, right_col = st.columns(2)

    with left_col:
        st.markdown("#### 🏫 Department-wise Students")
        department_counts = (
            df.groupby("department")
            .size()
            .reset_index(name="Students")
        )

        department_chart = px.bar(
            department_counts,
            x="department",
            y="Students",
            color="department",
            title="Student Distribution by Department",
            labels={
                "department": "Department",
                "Students": "Number of Students"
            }
        )

        department_chart.update_layout(
            showlegend=False,
            xaxis_title="Department",
            yaxis_title="Number of Students"
        )

        st.plotly_chart(
            department_chart,
            use_container_width=True
        )

    with right_col:
        st.markdown("#### 📚 Year-wise Students")
        year_counts = (
            df.groupby("year")
            .size()
            .reset_index(name="Students")
        )

        year_chart = px.bar(
            year_counts,
            x="year",
            y="Students",
            title="Student Distribution by Academic Year",
            labels={
                "year": "Year of Study",
                "Students": "Number of Students"
            }
        )

        year_chart.update_layout(
            xaxis_title="Year of Study",
            yaxis_title="Number of Students",
            xaxis=dict(
                tickmode="linear",
                dtick=1
            )
        )

        st.plotly_chart(
            year_chart,
            use_container_width=True
        )

else:
    st.info(
        "No student records are available yet. "
        "Open Student Management from the sidebar to register your first student."
    )

st.divider()


# ==========================================
# ACADEMIC PERFORMANCE
# ==========================================

st.subheader("📝 Academic Performance")

with get_connection() as conn:
    marks_df = pd.read_sql_query(
        """
        SELECT
            s.roll_number,
            s.name,
            s.department,
            m.subject,
            m.marks
        FROM marks m
        INNER JOIN students s
            ON s.id = m.student_id
        ORDER BY s.name
        """,
        conn
    )

if not marks_df.empty:
    col1, col2 = st.columns(2)

    with col1:
        department_performance = (
            marks_df.groupby("department")["marks"]
            .mean()
            .reset_index()
        )

        department_chart = px.bar(
            department_performance,
            x="department",
            y="marks",
            color="department",
            title="Average Marks by Department",
            labels={
                "department": "Department",
                "marks": "Average Marks"
            }
        )

        department_chart.update_layout(
            showlegend=False,
            yaxis_range=[0, 100]
        )

        st.plotly_chart(
            department_chart,
            use_container_width=True
        )

    with col2:
        marks_chart = px.histogram(
            marks_df,
            x="marks",
            nbins=10,
            title="Distribution of Subject Marks",
            labels={
                "marks": "Marks",
                "count": "Number of Records"
            }
        )

        marks_chart.update_layout(
            xaxis_range=[0, 100],
            xaxis_title="Marks",
            yaxis_title="Number of Records"
        )

        st.plotly_chart(
            marks_chart,
            use_container_width=True
        )

else:
    st.info(
        "Academic charts will appear after you enter marks in the Marks Management page."
    )

st.divider()


# ==========================================
# RECENT STUDENT REGISTRATIONS
# ==========================================

st.subheader("👨‍🎓 Recent Student Registrations")

if students:
    recent_students = pd.DataFrame(students)
    recent_students = recent_students[
        [
            "roll_number",
            "name",
            "email",
            "department",
            "year"
        ]
    ].head(10)

    recent_students = recent_students.rename(
        columns={
            "roll_number": "Roll Number",
            "name": "Student Name",
            "email": "Email",
            "department": "Department",
            "year": "Year"
        }
    )

    st.dataframe(
        recent_students,
        use_container_width=True,
        hide_index=True
    )

else:
    st.write("Student registrations will appear here once you add students.")

st.divider()


# ==========================================
# TOP PERFORMERS
# ==========================================

st.subheader("🏆 Top Student Performers")

if not marks_df.empty:
    student_averages = (
        marks_df.groupby(
            ["roll_number", "name", "department"]
        )["marks"]
        .mean()
        .reset_index()
        .rename(
            columns={"marks": "Average Marks"}
        )
        .sort_values(
            "Average Marks",
            ascending=False
        )
        .head(5)
    )

    student_averages.insert(
        0,
        "Rank",
        range(1, len(student_averages) + 1)
    )

    st.dataframe(
        student_averages.round(
            {"Average Marks": 2}
        ),
        use_container_width=True,
        hide_index=True
    )

else:
    st.info("Top performers will appear when student marks are available.")


# ==========================================
# FOOTER
# ==========================================

st.markdown(
    """
    <div class="dashboard-footer">
        StudentHub Pro | Smart Student Management System<br>
        Academic Records • Course Management • Performance Tracking
    </div>
    """,
    unsafe_allow_html=True
)
