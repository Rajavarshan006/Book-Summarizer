import bcrypt
from utils.database import create_user, get_user_by_email

def register_user(name, email, password):
    # Basic validation (backend must always validate)
    if not name or not email or not password:
        return False, "All fields are required."

    # Normalize email
    email = email.strip().lower()

    # Check if user exists
    existing_user = get_user_by_email(email)
    if existing_user:
        return False, "User already exists with this email"

    # Hash password
    hashed_pw = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode('utf-8')

    # Save user
    user_id = create_user(name, email, hashed_pw, role="user")
    
    return True, "User registered successfully"

def login_user(email, password):
    if not email or not password:
        return False, "Email and password are required."

    # Normalize email
    email = email.strip().lower()

    user = get_user_by_email(email)
    if not user:
        return False, "User not found with this email"

    stored_hash = user.get("password_hash", "")

    # Check password
    if bcrypt.checkpw(password.encode(), stored_hash.encode('utf-8')):
        return True, user

    return False, "Incorrect password."
