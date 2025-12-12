import streamlit as st
import re
from backend.auth import register_user


def load_css():
    try:
        with open("styles/styles.css") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    except:
        st.warning("styles.css not found. UI will load without custom styles.")


# ----------------------
# VALIDATION FUNCTIONS
# ----------------------
def validate_name(name):
    return bool(re.match(r"^[A-Za-z ]{2,}$", name))


def validate_email(email):
    pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    return bool(re.match(pattern, email))


def validate_password(password):
    pattern = r"^(?=.*[A-Z])(?=.*[a-z])(?=.*[0-9])(?=.*[!@#$%^&*]).{8,}$"
    return bool(re.match(pattern, password))


# ----------------------
# REGISTER PAGE
# ----------------------
def register_page():
    load_css()
    st.title("Create an Account")

    first_name = st.text_input("First Name")
    last_name = st.text_input("Last Name")
    email = st.text_input("Email Address")
    password = st.text_input("Password", type="password")
    confirm = st.text_input("Confirm Password", type="password")

    # error holders
    first_error = ""
    last_error = ""
    email_error = ""
    password_error = ""
    confirm_error = ""

    # ----------------------
    # SIGNUP BUTTON CLICK
    # ----------------------
    if st.button("Signup", key="signup_btn"):
        # validation
        if not validate_name(first_name):
            first_error = "First name must only contain letters and spaces, min 2 characters."

        if not validate_name(last_name):
            last_error = "Last name must only contain letters and spaces, min 2 characters."

        if not validate_email(email):
            email_error = "Enter a valid email address."

        if not validate_password(password):
            password_error = "Password must have at least 8 characters with uppercase, lowercase, number, and special character."

        if password != confirm:
            confirm_error = "Passwords do not match."

        # if any error → show them
        if first_error or last_error or email_error or password_error or confirm_error:
            st.error("Please fix the errors below.")
        else:
            full_name = f"{first_name.strip()} {last_name.strip()}"
            email_clean = email.strip().lower()

            success, msg = register_user(full_name, email_clean, password)

            if success:
                st.success(msg)
                st.info("Redirecting to login page...")

                # navigate to login
                st.session_state["current_page"] = "login"
                st.rerun()
            else:
                st.error(msg)

    # ----------------------
    # NAVIGATE TO LOGIN
    # ----------------------
    if st.button("Already have an account? Login here", key="go_login_btn"):
        st.session_state["current_page"] = "login"
        st.rerun()

    # ----------------------
    # SHOW VALIDATION ERRORS
    # ----------------------
    if first_error:
        st.warning(first_error)
    if last_error:
        st.warning(last_error)
    if email_error:
        st.warning(email_error)
    if password_error:
        st.warning(password_error)
    if confirm_error:
        st.warning(confirm_error)
