import streamlit as st
from backend.auth import login_user
from backend.session import login_session

def login_page():
    st.title("Login")

    email = st.text_input("Email Address")
    password = st.text_input("Password", type="password")

    email_error = ""
    password_error = ""

    if st.button("Login"):
        if not email:
            email_error = "Email cannot be empty"

        if not password:
            password_error = "Password cannot be empty"

        if email_error or password_error:
            st.error("Please correct the errors below")
        else:
            success, result = login_user(email, password)

            if success:
                user = result
                login_session(user)
                st.success("Login successful")
                st.rerun()    # Move to dashboard
            else:
                st.error(result)

    if email_error:
        st.warning(email_error)

    if password_error:
        st.warning(password_error)
