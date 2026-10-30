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
    get_student_attendance_records
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
