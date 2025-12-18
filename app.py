import streamlit as st
from frontend.login import login_page
from frontend.register import register_page
from frontend.landing import landing_page      # ADD YOUR LANDING PAGE
from backend.session import is_logged_in, logout_session
from frontend.upload_book import upload_book_page
from frontend.dashboard import dashboard_page
from frontend.uploaded_books_page import uploaded_books_page


def main():

    # -----------------------------------------
    # INITIAL PAGE SHOULD BE LANDING PAGE
    # -----------------------------------------
    if "current_page" not in st.session_state:
        st.session_state["current_page"] = "landing"   # FIXED

    page = st.session_state["current_page"]

    # -----------------------------------------
    # USER NOT LOGGED IN
    # -----------------------------------------
    if not is_logged_in():

        if page == "landing":
            landing_page()

        elif page == "login":
            login_page()

        elif page == "register":
            register_page()

        else:
            # fallback safety
            st.session_state["current_page"] = "landing"
            st.rerun()

    # -----------------------------------------
    # USER IS LOGGED IN
    # -----------------------------------------
    else:
        st.sidebar.title("Navigation")

        if st.sidebar.button("Dashboard"):
            st.session_state["current_page"] = "dashboard"

        if st.sidebar.button("Uploaded Books"):
            st.session_state["current_page"] = "uploaded_books"
            st.rerun()

        if st.sidebar.button("Upload Book"):
            st.session_state["current_page"] = "upload"

        if st.sidebar.button("Logout"):
            logout_session()
            st.session_state["current_page"] = "landing"   # go back to landing after logout
            st.rerun()

        # Routing
        if page == "dashboard":
            dashboard_page()
        elif page == "uploaded_books":
            uploaded_books_page()
        elif page == "upload":
            upload_book_page()

        else:
            st.session_state["current_page"] = "dashboard"
            st.rerun()


if __name__ == "__main__":
    main()
