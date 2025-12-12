import streamlit as st
from backend.auth import login_user      # using your existing auth.py
from backend.session import login_session

def load_css():
    try:
        with open("styles/styles.css") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    except:
        st.warning("styles.css not found. UI will load without custom styles.")

def login_page():
    load_css()
    st.title("Login")

    # Input fields
    email = st.text_input("Email Address")
    password = st.text_input("Password", type="password")

    # Error variables
    email_error = ""
    password_error = ""

    # --------------------------
    # LOGIN BUTTON CLICK
    # --------------------------
    if st.button("Login", key="btn_login"):
        # Validate inputs
        if not email:
            email_error = "Email cannot be empty"

        if not password:
            password_error = "Password cannot be empty"

        # If validation fails
        if email_error or password_error:
            st.error("Please correct the errors below")
        else:
            # Call your backend login function
            success, result = login_user(email, password)

            if success:
                user = result  # user dictionary
                login_session(user)  # save to session

                # Set navigation page
                st.session_state["current_page"] = "dashboard"
                st.success("Login successful!")
                st.rerun()
            else:
                # result contains the error message
                st.error(result)

    # --------------------------
    # DISPLAY FIELD ERROR MESSAGES
    # --------------------------
    if email_error:
        st.warning(email_error)

    if password_error:
        st.warning(password_error)

    # --------------------------
    # REGISTER REDIRECT BUTTON
    # --------------------------
    if st.button("New user? Create an account", key="btn_register"):
        st.session_state["current_page"] = "register"
        st.rerun()

    # --------------------------
    # EXTRA UI LINK
    # --------------------------
    st.markdown(
        '<div class="sub-link" style="margin-top: 10px;">Forgot Password?</div>',
        unsafe_allow_html=True
    )
