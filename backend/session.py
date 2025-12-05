import streamlit as st

# -----------------------------
# SESSION MANAGEMENT FUNCTIONS
# -----------------------------

def login_session(user):
  st.session_state['logged_in'] = True
  st.session_state['user_id'] = str(user['_id'])
  st.session_state['user_name'] = user['name']
  st.session_state['user_email'] = user['email']
  st.session_state['user_role'] = user.get('role', 'user')


def logout_session():
  for key in ["logged_in","user_name","user_id","user_email", "user_role"]:
    if key in st.session_state:
      del st.session_state[key]


def is_logged_in():
  return st.session_state.get('logged_in', False)

def get_current_user():
  if is_logged_in():
    return {
      'user_id': st.session_state['user_id'],
      'name': st.session_state['user_name'],
      'email': st.session_state['user_email'],
      'role': st.session_state.get('user_role', 'user')
    }
  return None  

