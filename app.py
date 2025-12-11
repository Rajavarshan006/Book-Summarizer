import streamlit as st
from frontend.login import login_page
from frontend.register import register_page
from backend.session import is_logged_in, logout_session
from frontend.upload_book import upload_book_page
from frontend.dashboard import dashboard_page



def main():

    # Initialize navigation state
    if "current_page" not in st.session_state:
        st.session_state["current_page"] = "login"

    # User not logged in
    if not is_logged_in():

        # Show Login Page
        if st.session_state["current_page"] == "login":
            login_page()

        # Show Register Page
        elif st.session_state["current_page"] == "register":
            register_page()

    # User is logged in
    else:
        st.sidebar.title("Navigation")

        if st.sidebar.button("Dashboard"):
            st.session_state["current_page"] = "dashboard"

        if st.sidebar.button("Upload Book"):
            st.session_state["current_page"] = "upload"

        if st.sidebar.button("Logout"):
            logout_session()
            st.session_state["current_page"] = "login"
            st.rerun()

        # Page routing
        if st.session_state["current_page"] == "dashboard":
            dashboard_page()

        elif st.session_state["current_page"] == "upload":
            upload_book_page()



if __name__ == "__main__":
    main()
