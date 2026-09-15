import os
import re
import hashlib
import sqlite3


# Database location
DB_FILE = os.path.join("data", "users.db")


def get_connection():
    """Create and return a database connection."""
    os.makedirs("data", exist_ok=True)
    return sqlite3.connect(DB_FILE)


def create_database():
    """Create the users table if it does not already exist."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    """)

    conn.commit()
    conn.close()


def init_db():
    """Compatibility function."""
    create_database()


def hash_password(password):
    """Hash password before storing it."""
    return hashlib.sha256(
        password.encode("utf-8")
    ).hexdigest()


def register_user(name, email, password):
    """Register a new user."""

    name = name.strip()
    email = email.strip().lower()

    # -----------------------------
    # Full Name Validation
    # -----------------------------
    if not name:
        return False, "Please enter your full name."

    # Name must contain letters
    if not re.search(r"[A-Za-z]", name):
        return False, "Full name must contain letters."

    # Name cannot contain numbers
    if re.search(r"\d", name):
        return False, "Full name should not contain numbers."

    # -----------------------------
    # Gmail Validation
    # -----------------------------
    gmail_pattern = (
        r"^[A-Za-z][A-Za-z0-9._%+-]*@gmail\.com$"
    )

    if not re.fullmatch(gmail_pattern, email):
        return (
            False,
            "Please use a valid Gmail address ending with @gmail.com."
        )

    # -----------------------------
    # Password Validation
    # -----------------------------
    if not password:
        return False, "Please enter a password."

    if len(password) < 6:
        return False, "Password must be at least 6 characters long."

    # -----------------------------
    # Create Database
    # -----------------------------
    create_database()

    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute(
            """
            INSERT INTO users (name, email, password)
            VALUES (?, ?, ?)
            """,
            (
                name,
                email,
                hash_password(password)
            )
        )

        conn.commit()

        return True, "Registration successful!"

    except sqlite3.IntegrityError:
        return (
            False,
            "An account with this Gmail already exists."
        )

    finally:
        conn.close()


def login_user(email, password):
    """Authenticate an existing user."""

    email = email.strip().lower()

    create_database()

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT name, password
        FROM users
        WHERE email = ?
        """,
        (email,)
    )

    user = cursor.fetchone()

    conn.close()

    if user is None:
        return (
            False,
            "",
            "Invalid Gmail or password."
        )

    stored_name, stored_password = user

    if hash_password(password) != stored_password:
        return (
            False,
            "",
            "Invalid Gmail or password."
        )

    return (
        True,
        stored_name,
        "Login successful."
    )


# Create database when application starts
create_database()