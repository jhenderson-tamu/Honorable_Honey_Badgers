
import sqlite3 as sql
import bcrypt as bc
from datetime import datetime

def setup_user_db():
    """Set up the user database with users and logon_history tables"""
    with sql.connect("data/users.db") as conn:
        cursor = conn.cursor()
        # Create the users table to store username and password
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users ( 
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL )""")
        #Create logon history table to store login history
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS logon_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL,
                action TEXT NOT NULL,
                timestamp TEXT NOT NULL)""")

def setup_finance_db():
    """Set up the finance database with expenses and income tables"""
    with sql.connect("data/finance.db") as conn:
        cursor = conn.cursor()
        # Create table to store expenses
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS expenses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT NOT NULL,
                category TEXT NOT NULL,
                amount REAL NOT NULL,
                description TEXT,
                username TEXT NOT NULL)""")
        # Create table to store income
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS income (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT NOT NULL,
                category TEXT NOT NULL,
                amount REAL NOT NULL,
                description TEXT,
                username TEXT NOT NULL)""")
        # Create table to store expense_category to provide drop-down menu
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS expense_category (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name UNIQUE NOT NULL)""")
        # Create table to store income_category to provide drop-down menu
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS income_category (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name UNIQUE NOT NULL)""")

def initialize_expense_categories():
    """Initialize default expense categories"""
    conn = sql.connect("data/finance.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS expense_category (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL)""")
    # Provide default expense categories
    default_categories = ["Food", "Transportation", "Utilities", "Entertainment",
                          "Healthcare", "Other"]
    for cat in default_categories:
        cursor.execute("INSERT OR IGNORE INTO expense_category (name) VALUES (?)", (cat,))
    conn.commit()
    conn.close()

def initialize_income_categories():
    """Initialize default income categories"""
    conn = sql.connect("data/finance.db")
    cursor = conn.cursor()
    # Provide default income categories
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS income_category (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL)""")
    default_categories = ["Salary/Wages", "Investment Income", "Reimbursement", "Gifts"]
    for cat in default_categories:
        cursor.execute("INSERT OR IGNORE INTO income_category (name) VALUES (?)", (cat,))
    conn.commit()
    conn.close()

def log_user_action(username, action):
    """Log user actions to the database"""
    with sql.connect("data/users.db") as conn:
        cursor = conn.cursor()
        cursor.execute("INSERT INTO logon_history (username, action, timestamp) VALUES (?, ?, ?)",
                       (username, action, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
        conn.commit()

def register_user(username, password):
    """Register a new user with hashed password"""
    if not username or not password:
        return "Error! All fields are required!"
    
    # Create a password that is both hashed and salted
    hashed_pw = bc.hashpw(password.encode("utf-8"), bc.gensalt())
    
    try:
        conn = sql.connect("data/users.db")
        cursor = conn.cursor()
        cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", 
                       (username, hashed_pw))
        conn.commit()
        conn.close()
        return "User registered successfully!"
    except sql.IntegrityError:
        return "Error! Username already exists!"

def authenticate_user(username, password):
    """Authenticate user login"""
    if not username or not password:
        return False, "Error! All fields are required!"
    
    conn = sql.connect("data/users.db")
    cursor = conn.cursor()
    cursor.execute("SELECT password FROM users WHERE username = ?", (username,))
    result = cursor.fetchone()
    conn.close()
    
    if result and bc.checkpw(password.encode("utf-8"), result[0]):
        return True, "Login successful!"
    else:
        return False, "Invalid username or password!"

def change_user_password(username, old_password, new_password):
    """Change user password after verifying old password"""
    if not old_password or not new_password:
        return False, "Both fields are required!"
    
    conn = sql.connect("data/users.db")
    cursor = conn.cursor()
    cursor.execute("SELECT password FROM users WHERE username=?", (username,))
    result = cursor.fetchone()
    
    if result and bc.checkpw(old_password.encode("utf-8"), result[0]):
        hashed_new = bc.hashpw(new_password.encode("utf-8"), bc.gensalt())
        cursor.execute("UPDATE users SET password=? WHERE username=?", 
                       (hashed_new, username))
        conn.commit()
        conn.close()
        return True, "Password updated successfully!"
    else:
        conn.close()
        return False, "Old password incorrect!"

def get_user_login_history(username, limit=10):
    """Get user login history"""
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