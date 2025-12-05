import bcrypt
from utils.database import create_user,get_user_by_email

def register_user(name, email, password):
    existing_user = get_user_by_email(email)
    if existing_user:
        return False, "User already exists"
    password_hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

    create_user(name, email, password_hash)
    return True, "Registered successfully"


def login_user(email, password):
    user = get_user_by_email(email)
    if not user:
        return False, "User not found with this email"
    stored_hash = user['password_hash']

    if bcrypt.checkpw(password.encode(), stored_hash.encode('utf-8')):
        return True, user
    return False, "Incorrect password."