# PROGRAM: Database Setup and User Authentication
# PURPOSE:
#   Manage database creation, category initialization, user registration,
#   authentication, password updates, and login history tracking.
# INPUT:
#   - Usernames, passwords, and user actions passed to functions.
# PROCESS:
#   - Interacts with SQLite databases (`users.db` and `finance.db`).
#   - Creates tables, inserts default categories, and stores/retrieves
#     authentication and financial data.
# OUTPUT:
#   - Database tables created (if not already existing).
#   - Default categories populated.
#   - User credentials securely stored.
#   - Authentication success/failure messages returned.
#   - Login history records retrieved.
# HONOR CODE:
#   On my honor, as an Aggie, I have neither given nor received
#   unauthorized aid on this academic work.

import sqlite3 as sql
import bcrypt as bc
from datetime import datetime


def setup_user_db() -> None:
    """
    Create the user database with tables if they do not exist.

    Tables created:
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
    Create the finance database with expense, income, and category tables.

    Tables created:
        - expenses: Stores all expense transactions.
        - income: Stores all income transactions.
        - expense_category: Stores available expense categories.
        - income_category: Stores available income categories.
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
    Insert default expense categories into the database if not already present.

    Default categories include:
        - Food, Transportation, Utilities, Entertainment,
          Healthcare, Other.
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
    Insert default income categories into the database if not already present.

    Default categories include:
        - Salary/Wages, Investment Income,
          Reimbursement, Gifts.
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
    Insert a user action into the logon_history table.

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
    Register a new user with a hashed password.

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
    Verify user login credentials.

    Args:
        username (str): Username.
        password (str): Plaintext password.

    Returns:
        tuple: (success, message)
            - success (bool): True if authentication succeeds.
            - message (str): Feedback message.
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
    Update a user's password after validating their current password.

    Args:
        username (str): Username.
        old_password (str): Current password.
        new_password (str): New password to store.

    Returns:
        tuple: (success, message)
            - success (bool): True if update was successful.
            - message (str): Feedback message.
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
    Retrieve recent login history for a specific user.

    Args:
        username (str): Username to filter by.
        limit (int, optional): Number of records to return. Defaults to 10.

    Returns:
        list[tuple]: (action, timestamp) pairs of user activity.
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
