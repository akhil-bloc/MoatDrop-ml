import sqlite3
from passlib.context import CryptContext
from typing import Optional
from .models import User, UserCreate

import os

# Use absolute path for DB_PATH
DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "proxy.db")
print(f"Using database at: {DB_PATH}")
# Use SHA256 instead of bcrypt to avoid the 72-byte limit
pwd_context = CryptContext(schemes=["sha256_crypt"], deprecated="auto")

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_user_by_email(email: str) -> Optional[User]:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM users WHERE email = ?", (email,))
    user_row = cursor.fetchone()
    conn.close()
    
    if user_row:
        return User(**dict(user_row))
    return None

def authenticate_user(email: str, password: str) -> Optional[User]:
    user = get_user_by_email(email)
    if not user:
        return None
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT password_hash FROM users WHERE email = ?", (email,))
    result = cursor.fetchone()
    conn.close()
    
    if not result:
        return None
        
    stored_hash = result[0]
    if not verify_password(password, stored_hash):
        return None
        
    return user

def create_user(user: UserCreate) -> User:
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    hashed_password = get_password_hash(user.password)
    
    cursor.execute(
        "INSERT INTO users (email, password_hash, is_active, tier) VALUES (?, ?, ?, ?)",
        (user.email, hashed_password, user.is_active, "basic")
    )
    
    user_id = cursor.lastrowid
    conn.commit()
    conn.close()
    
    return User(id=user_id, email=user.email, is_active=user.is_active, tier="basic")

def setup_users_table():
    """Create users table if it doesn't exist"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        email TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        is_active BOOLEAN NOT NULL DEFAULT 1,
        tier TEXT NOT NULL DEFAULT 'basic'
    )
    """)
    
    conn.commit()
    conn.close()
