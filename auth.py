import streamlit as st
import hmac
from database import get_connection

def check_admin_credentials(username, password):
    """Verify administrator credentials against Streamlit secrets."""
    try:
        correct_user = st.secrets["admin_username"]
        correct_pass = st.secrets["admin_password"]
        return hmac.compare_digest(username, correct_user) and hmac.compare_digest(password, correct_pass)
    except Exception:
        st.error("Login configuration missing. Please configure secrets in Streamlit Cloud Dashboard.")
        return False

def verify_student_credentials(roll_number, password):
    """Verify student credentials strictly against database."""
    cleaned_roll = str(roll_number).strip().upper()
    cleaned_pwd = str(password).strip()

    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM students WHERE UPPER(TRIM(roll_number)) = ?", (cleaned_roll,))
        row = cursor.fetchone()
        
        if row:
            student = dict(row)
            # Fetch strictly from DB; only default if column was truly NULL/empty
            db_pwd = str(student.get("password") or "").strip()
            if not db_pwd:
                db_pwd = "student123"
            
            # Strict single-match comparison
            if hmac.compare_digest(cleaned_pwd, db_pwd):
                return student
    return None

def login_form():
    """Renders dual-role login interface."""
    st.markdown("""
    <div style="text-align: center; margin-bottom: 25px;">
        <h1 style="color: #f8fafc; font-weight: 800; margin: 0; font-size: 38px;">
            StudentHub<span style="color: #38bdf8;">.Pro</span>
        </h1>
        <p style="color: #94a3b8; font-size: 15px;">Secure Academic Portal & Institutional Management</p>
    </div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        tab_admin, tab_student = st.tabs(["🔐 Administrator Login", "👨‍🎓 Student Portal Login"])

        # ----------------- ADMIN LOGIN -----------------
        with tab_admin:
            with st.form("admin_login_form"):
                st.markdown("##### Administrative Credentials")
                user = st.text_input("Username", placeholder="e.g. admin")
                pwd = st.text_input("Password", type="password", placeholder="••••••••")
                submit_admin = st.form_submit_button("Log In as Administrator", use_container_width=True)

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
                st.markdown("##### Student Credentials")
                roll_no = st.text_input("Roll Number", placeholder="e.g. 2505A31016")
                student_pwd = st.text_input("Password", type="password", placeholder="Default: student123")
                submit_student = st.form_submit_button("Log In to Student Portal", use_container_width=True)

                if submit_student:
                    if not roll_no.strip() or not student_pwd.strip():
                        st.warning("Please provide both Roll Number and Password.")
                    else:
                        student_rec = verify_student_credentials(roll_no, student_pwd)
                        if student_rec:
                            st.session_state["authenticated"] = True
                            st.session_state["role"] = "student"
                            st.session_state["student_info"] = student_rec
                            st.session_state["user_display"] = student_rec["name"]
                            st.rerun()
                        else:
                            st.error("Invalid Roll Number or Password. (Default is student123)")

def require_login():
    if not st.session_state.get("authenticated", False):
        login_form()
        st.stop()

def logout_button():
    if not st.session_state.get("authenticated", False):
        return

    if st.session_state.get("_logout_rendered", False):
        return

    if st.sidebar.button("🚪 Logout", key="app_global_logout_btn", use_container_width=True):
        st.session_state.clear()
        st.rerun()

    st.session_state["_logout_rendered"] = True
