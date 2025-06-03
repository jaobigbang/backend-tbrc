# models/user.py

# ใช้ dict เป็น mock DB
from auth.auth_handler import get_password_hash

fake_users_db = {
    "admin": {
        "username": "admin",
        "hashed_password": get_password_hash("adminpass"),
        "role": "admin"
    },
    "user": {
        "username": "user",
        "hashed_password": get_password_hash("userpass"),
        "role": "user"
    }
}
