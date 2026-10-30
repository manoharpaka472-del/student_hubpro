import streamlit as st
import hmac
from database import get_all_students, get_connection

def check_admin_credentials(username, password):
    """Verify administrator credentials against Streamlit secrets."""
    try:
        correct_user = st.secrets["admin_username"]
        correct_pass = st.secrets["admin_password"]
        return hmac.compare_digest(username, correct_user) and hmac.compare_digest(password, correct_pass)
    except Exception:
        st.error("Login configuration is missing. Please configure application secrets in Streamlit Cloud.")
        return False

def verify_student(roll_number):
    """Verify student existence in the database by roll number."""
    students = get_all_students()
    for student in students:
        if str(student["roll_number"]).strip().upper() == str(roll_number).strip().upper():
            return student
    return None

def login_form():
    """Renders a modern dual-role login interface."""
    st.markdown("""
    <div style="text-align: center; margin-bottom: 25px;">
        <h1 style="color: #f8fafc; font-weight: 800; margin: 0;">StudentHub<span style="color: #38bdf8;">.Pro</span></h1>
        <p style="color: #94a3b8; font-size: 14px;">Smart Student Management & Academic Portal</p>
    </div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        tab_admin, tab_student = st.tabs(["🔐 Administrator Login", "👨‍🎓 Student Portal Login"])

        # ----------------- ADMIN LOGIN -----------------
        with tab_admin:
            with st.form("admin_login_form"):
                st.markdown("#### Admin Authentication")
                user = st.text_input("Username", placeholder="e.g. admin")
                pwd = st.text_input("Password", type="password", placeholder="••••••••")
                submit_admin = st.form_submit_button("Log In as Admin", use_container_width=True)

                if submit_admin:
                    if check_admin_credentials(user, pwd):
                        st.session_state["authenticated"] = True
                        st.session_state["role"] = "admin"
                        st.session_state["user_display"] = "Administrator"
                        st.rerun()
                    else:
                        st.error("Invalid administrator credentials.")

        # ----------------- STUDENT LOGIN -----------------
        with tab_student:
            with st.form("student_login_form"):
                st.markdown("#### Student Authentication")
                roll_no = st.text_input("Enter Registered Roll Number", placeholder="e.g. 2505A31016")
                submit_student = st.form_submit_button("Log In to Student Portal", use_container_width=True)

                if submit_student:
                    if not roll_no.strip():
                        st.warning("Please enter your roll number.")
                    else:
                        student_rec = verify_student(roll_no)
                        if student_rec:
                            st.session_state["authenticated"] = True
                            st.session_state["role"] = "student"
                            st.session_state["student_info"] = student_rec
                            st.session_state["user_display"] = student_rec["name"]
                            st.rerun()
                        else:
                            st.error("Roll number not found. Please contact the administrator.")

def require_login():
    """Halts execution if the user is not authenticated."""
    if not st.session_state.get("authenticated", False):
        login_form()
        st.stop()

def logout_button():
    """Renders a single safe logout button in the sidebar."""
    if not st.session_state.get("authenticated", False):
        return

    if st.session_state.get("_logout_rendered", False):
        return

    if st.sidebar.button("🚪 Logout", key="app_global_logout_btn", use_container_width=True):
        st.session_state.clear()
        st.rerun()

    st.session_state["_logout_rendered"] = True
