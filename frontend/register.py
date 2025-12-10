import streamlit as st
import re
from backend.auth import register_user
def load_css():
    with open("styles/styles.css") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

def validate_name(name):
    return bool(re.match(r"^[A-Za-z ]{2,}$", name))

def validate_email(email):
    pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    return bool(re.match(pattern, email))

def validate_password(password):
    pattern = r"^(?=.*[A-Z])(?=.*[a-z])(?=.*[0-9])(?=.*[!@#$%^&*]).{8,}$"
    return bool(re.match(pattern, password))

def register_page():
    load_css()
    st.title("Create an Account")

    first_name = st.text_input("First Name")
    last_name = st.text_input("Last Name")
    email = st.text_input("Email Address")
    password = st.text_input("Password", type="password")
    confirm = st.text_input("Confirm Password", type="password")

    first_error = ""
    last_error = ""
    email_error = ""
    password_error = ""
    confirm_error = ""

    if st.button("Signup"):
        if not validate_name(first_name):
            first_error = "First name must have only letters and spaces. minimum 2 characters"

        if not validate_name(last_name):
            last_error = "Last name must have only letters and spaces. minimum 2 characters"

        if not validate_email(email):
            email_error = "Enter a valid email address"

        if not validate_password(password):
            password_error = "Password must have minimum 8 characters. one uppercase. one lowercase. one number. one special character"

        if password != confirm:
            confirm_error = "Passwords do not match"

        if first_error or last_error or email_error or password_error or confirm_error:
            st.error("Please fix the errors below")
        else:
            full_name = first_name + " " + last_name
            success, msg = register_user(full_name, email, password)

            if success:
                st.success(msg)
                st.info("You can now log in")
                st.rerun()
            else:
                st.error(msg)
    if st.button("Already have an account? Login here"):
      st.session_state["current_page"] = "login"
      st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)


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
