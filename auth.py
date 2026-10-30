import hmac
import streamlit as st


def require_login():

    # Already authenticated?
    if st.session_state.get("authenticated", False):
        return

    st.set_page_config(
        page_title="StudentHub Pro Login",
        page_icon="🎓",
        layout="centered"
    )

    st.markdown(
        """
        <h1 style="text-align:center;">🎓 StudentHub Pro</h1>
        <p style="text-align:center;">
            Smart Student Management System
        </p>
        """,
        unsafe_allow_html=True
    )

    st.divider()

    with st.form("login_form"):

        st.subheader("Administrator Login")

        username = st.text_input("Username")

        password = st.text_input(
            "Password",
            type="password"
        )

        submitted = st.form_submit_button(
            "Login",
            use_container_width=True,
            type="primary"
        )

        if submitted:

            try:
                expected_username = st.secrets["admin_username"]
                expected_password = st.secrets["admin_password"]

                username_ok = hmac.compare_digest(
                    username,
                    expected_username
                )

                password_ok = hmac.compare_digest(
                    password,
                    expected_password
                )

                if username_ok and password_ok:
                    st.session_state["authenticated"] = True
                    st.rerun()

                else:
                    st.error("Invalid username or password.")

            except Exception:
                st.error(
                    "Login configuration is missing. "
                    "Please configure the application secrets."
                )

    st.stop()


def logout_button():
    # Only render the logout button if user is authenticated and it hasn't rendered yet
    if not st.session_state.get("authenticated", False):
        return

    # Check flag to ensure button only renders once per run
    if st.session_state.get("_logout_rendered", False):
        return

    if st.sidebar.button("🚪 Logout", key="global_logout_btn"):
        st.session_state["authenticated"] = False
        st.session_state["_logout_rendered"] = False
        st.rerun()

    st.session_state["_logout_rendered"] = True
