import bcrypt
from utils.database import create_user,get_user_by_email

def register_user(name, email, password):
    existing_user = get_user_by_email(email)
    print(f"DEBUG: Checking email {email}, existing_user: {existing_user}")

    if existing_user:
        return False, "User already exists with this email"

    hashed_pw = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode('utf-8')

    user_id = create_user(name, email, hashed_pw, role="user")
    print(f"DEBUG: Created user with ID: {user_id}")
    
    return True, "User registered successfully"


def login_user(email, password):
    user = get_user_by_email(email)
    if not user:
        return False, "User not found with this email"
    stored_hash = user['password_hash']

    if bcrypt.checkpw(password.encode(), stored_hash.encode('utf-8')):
        return True, user
    return False, "Incorrect password."