import streamlit as st
import hmac
from collections.abc import Mapping


def check_password():
    """Render a login form and return whether this session is authenticated."""
    if st.session_state.get("authenticated", False):
        return True

    if "users" in st.secrets:
        configured_users = st.secrets["users"]
        if not isinstance(configured_users, Mapping) or not configured_users:
            st.error("Login is not configured correctly: `[users]` must contain username/password entries.")
            return False
        if any(
            not isinstance(username, str)
            or not username
            or not isinstance(password, str)
            or not password
            for username, password in configured_users.items()
        ):
            st.error("Every `[users]` entry must have a non-empty username and password.")
            return False
        users = dict(configured_users)
    elif "username" in st.secrets and "password" in st.secrets:
        expected_username = st.secrets["username"]
        expected_password = st.secrets["password"]
        if (
            not isinstance(expected_username, str)
            or not expected_username
            or not isinstance(expected_password, str)
            or not expected_password
        ):
            st.error("Login secrets `username` and `password` must be non-empty strings.")
            return False
        users = {expected_username: expected_password}
    else:
        st.error("Login is not configured. Add a `[users]` table to Streamlit secrets.")
        return False

    def authenticate():
        username = st.session_state.get("login_username", "")
        password = st.session_state.get("login_password", "")
        matched_username = next(
            (
                configured_username
                for configured_username in users
                if hmac.compare_digest(
                    username.encode("utf-8"), configured_username.encode("utf-8")
                )
            ),
            None,
        )
        password_matches = matched_username is not None and hmac.compare_digest(
            password.encode("utf-8"), users[matched_username].encode("utf-8")
        )
        st.session_state["authenticated"] = password_matches
        if password_matches:
            st.session_state["authenticated_username"] = matched_username
        else:
            st.session_state.pop("authenticated_username", None)
        st.session_state["login_failed"] = not st.session_state["authenticated"]
        st.session_state.pop("login_username", None)
        st.session_state.pop("login_password", None)

    st.title("Log in")
    with st.form("login_form"):
        st.text_input("Username", key="login_username")
        st.text_input("Password", type="password", key="login_password")
        st.form_submit_button("Log in", on_click=authenticate)

    if st.session_state.get("login_failed", False):
        st.error("Username or password is incorrect.")

    if st.session_state.get("authenticated", False):
        st.session_state.pop("login_failed", None)
        return True

    return False
