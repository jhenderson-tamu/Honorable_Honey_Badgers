# PROGRAM: Database Setup and User Authentication
# PURPOSE: Define functions to set up databases, initialize default
# categories, log user activity, register users, authenticate logins,
# manage passwords, and retrieve login history.
# INPUT: Usernames, passwords, and user actions as function arguments.
# PROCESS: Interacts with SQLite databases to store and retrieve data.
# OUTPUT: Database tables created, records inserted/updated, authentication
# results, and login history.
# HONOR CODE: On my honor, as an Aggie, I have neither given nor
# received unauthorized aid on this academic work.

import sqlite3 as sql
import bcrypt as bc
from datetime import datetime


def setup_user_db() -> None:
    """
    Set up the user database with `users` and `logon_history` tables.

    Creates tables if they do not exist:
        - users: Stores username and hashed password.
        - logon_history: Stores user actions with timestamps.
    """
    with sql.connect("data/users.db") as conn:
        cursor = conn.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS logon_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL,
                action TEXT NOT NULL,
                timestamp TEXT NOT NULL
            )
        """)


def setup_finance_db() -> None:
    """
    Set up the finance database with tables for expenses, income,
    and their categories.
    """
    with sql.connect("data/finance.db") as conn:
        cursor = conn.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS expenses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT NOT NULL,
                category TEXT NOT NULL,
                amount REAL NOT NULL,
                description TEXT,
                username TEXT NOT NULL
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS income (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT NOT NULL,
                category TEXT NOT NULL,
                amount REAL NOT NULL,
                description TEXT,
                username TEXT NOT NULL
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS expense_category (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS income_category (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL
            )
        """)


def initialize_expense_categories() -> None:
    """
    Populate default expense categories if they do not already exist.
    """
    conn = sql.connect("data/finance.db")
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS expense_category (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL
        )
    """)

    default_categories = [
        "Food", "Transportation", "Utilities",
        "Entertainment", "Healthcare", "Other"
    ]

    for cat in default_categories:
        cursor.execute(
            "INSERT OR IGNORE INTO expense_category (name) VALUES (?)", (cat,)
        )

    conn.commit()
    conn.close()


def initialize_income_categories() -> None:
    """
    Populate default income categories if they do not already exist.
    """
    conn = sql.connect("data/finance.db")
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS income_category (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL
        )
    """)

    default_categories = [
        "Salary/Wages", "Investment Income",
        "Reimbursement", "Gifts"
    ]

    for cat in default_categories:
        cursor.execute(
            "INSERT OR IGNORE INTO income_category (name) VALUES (?)", (cat,)
        )

    conn.commit()
    conn.close()


def log_user_action(username: str, action: str) -> None:
    """
    Log a user action to the `logon_history` table.

    Args:
        username (str): Username performing the action.
        action (str): Description of the action performed.
    """
    with sql.connect("data/users.db") as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO logon_history (username, action, timestamp)
            VALUES (?, ?, ?)
        """, (username, action, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))

        conn.commit()


def register_user(username: str, password: str) -> str:
    """
    Register a new user with a securely hashed password.

    Args:
        username (str): Desired username.
        password (str): Plaintext password.

    Returns:
        str: Success or error message.
    """
    if not username or not password:
        return "Error! All fields are required!"

    hashed_pw = bc.hashpw(password.encode("utf-8"), bc.gensalt())

    try:
        conn = sql.connect("data/users.db")
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO users (username, password) VALUES (?, ?)",
            (username, hashed_pw)
        )
        conn.commit()
        conn.close()
        return "User registered successfully!"
    except sql.IntegrityError:
        return "Error! Username already exists!"


def authenticate_user(username: str, password: str) -> tuple[bool, str]:
    """
    Authenticate user login by verifying credentials.

    Args:
        username (str): Username.
        password (str): Plaintext password.

    Returns:
        tuple: (success, message)
            success (bool): True if authentication succeeds, else False.
            message (str): User feedback message.
    """
    if not username or not password:
        return False, "Error! All fields are required!"

    conn = sql.connect("data/users.db")
    cursor = conn.cursor()
    cursor.execute("SELECT password FROM users WHERE username = ?", (username,))
    result = cursor.fetchone()
    conn.close()

    if result and bc.checkpw(password.encode("utf-8"), result[0]):
        return True, "Login successful!"
    return False, "Invalid username or password!"


def change_user_password(username: str,
                         old_password: str,
                         new_password: str) -> tuple[bool, str]:
    """
    Change a user's password after validating the old password.

    Args:
        username (str): Username.
        old_password (str): Current password.
        new_password (str): New password to set.

    Returns:
        tuple: (success, message)
            success (bool): True if password was updated.
            message (str): User feedback message.
    """
    if not old_password or not new_password:
        return False, "Both fields are required!"

    conn = sql.connect("data/users.db")
    cursor = conn.cursor()
    cursor.execute("SELECT password FROM users WHERE username=?", (username,))
    result = cursor.fetchone()

    if result and bc.checkpw(old_password.encode("utf-8"), result[0]):
        hashed_new = bc.hashpw(new_password.encode("utf-8"), bc.gensalt())
        cursor.execute(
            "UPDATE users SET password=? WHERE username=?", (hashed_new, username)
        )
        conn.commit()
        conn.close()
        return True, "Password updated successfully!"

    conn.close()
    return False, "Old password incorrect!"


def get_user_login_history(username: str, limit: int = 10) -> list[tuple]:
    """
    Retrieve recent login history for a user.

    Args:
        username (str): Username to filter history by.
        limit (int, optional): Number of records to return. Defaults to 10.

    Returns:
        list[tuple]: List of (action, timestamp) tuples.
    """
    conn = sql.connect("data/users.db")
    cursor = conn.cursor()
    cursor.execute("""
        SELECT action, timestamp
        FROM logon_history
        WHERE username=?
        ORDER BY timestamp DESC
        LIMIT ?
    """, (username, limit))

    rows = cursor.fetchall()
    conn.close()
    return rows
