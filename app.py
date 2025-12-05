import streamlit as st
from frontend.login import login_page
from frontend.register import register_page
from backend.session import is_logged_in, logout_session

def main():
    st.sidebar.title("Navigation")

    if not is_logged_in():
        page = st.sidebar.selectbox("Go to", ["Login", "Register"])

        if page == "Login":
            login_page()

        if page == "Register":
            register_page()

    else:
        # User is logged in
        st.sidebar.write("Logged in")
        if st.sidebar.button("Logout"):
            logout_session()
            st.rerun()

        st.title("Dashboard")
        st.write("Welcome. you are logged in.")

if __name__ == "__main__":
    main()
