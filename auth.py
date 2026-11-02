import streamlit as st
from database import get_connection

def verify_student_credentials(roll_number, password):
    with get_connection() as conn:
        cursor = conn.cursor()
        cleaned_roll = str(roll_number).strip().upper()
        cursor.execute("SELECT * FROM students WHERE UPPER(TRIM(roll_number)) = ?", (cleaned_roll,))
        student = cursor.fetchone()

        if student:
            student_dict = dict(student)
            stored_pwd = (student_dict.get("password") or "student123").strip()
            if stored_pwd == str(password).strip():
                return student_dict
    return None

def login_form():
    st.markdown("""
    <div style="text-align: center; margin-bottom: 25px;">
        <h1 style="color: #ffffff; font-size: 32px; font-weight: 800; margin-bottom: 4px;">Academic Atelier</h1>
        <p style="color: #38bdf8; font-size: 14px; font-weight: 600; letter-spacing: 1px;">INSTITUTIONAL SUITE LOGIN</p>
    </div>
    """, unsafe_allow_html=True)

    tab_admin, tab_student = st.tabs(["🔐 Administrator Access", "👨‍🎓 Student Portal"])

    with tab_admin:
        with st.form("admin_login_box"):
            admin_user = st.text_input("Admin Username", placeholder="e.g. admin")
            admin_pwd = st.text_input("Admin Password", type="password", placeholder="••••••••")
            submit_admin = st.form_submit_button("Sign In as Administrator", use_container_width=True)

            if submit_admin:
                # Reads from Streamlit Secrets or defaults to standard local admin
                valid_admin = st.secrets.get("admin_username", "admin")
                valid_pwd = st.secrets.get("admin_password", "admin123")

                if admin_user.strip() == valid_admin and admin_pwd.strip() == valid_pwd:
                    st.session_state["authenticated"] = True
                    st.session_state["role"] = "admin"
                    st.session_state["user_name"] = "Administrator"
                    st.rerun()
                else:
                    st.error("Invalid administrator credentials.")

    with tab_student:
        with st.form("student_login_box"):
            roll = st.text_input("University Roll Number", placeholder="e.g. 2505A31016")
            pwd = st.text_input("Portal Password", type="password", placeholder="Default: student123")
            submit_student = st.form_submit_button("Sign In to Student Portal", use_container_width=True)

            if submit_student:
                student = verify_student_credentials(roll, pwd)
                if student:
                    st.session_state["authenticated"] = True
                    st.session_state["role"] = "student"
                    st.session_state["student_info"] = student
                    st.session_state["user_name"] = student["name"]
                    st.rerun()
                else:
                    st.error("Invalid Roll Number or Password.")

def require_login():
    if not st.session_state.get("authenticated", False):
        login_form()
        st.stop()

def logout_button():
    if st.sidebar.button("🚪 Logout", use_container_width=True):
        st.session_state.clear()
        st.rerun()
