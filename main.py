# PROGRAM: Personal Finance Application - Modular Version
# PURPOSE:
#   This is the main entry point for the personal finance application.
# INPUT:
#   - User login credentials
#   - Financial data inputs (expenses, income, budgets)
# PROCESS:
#   - Initialize required databases and default categories
#   - Authenticate the user through the login interface
#   - Launch the main GUI for financial management
# OUTPUT:
#   - A graphical user interface (GUI) for managing personal finance data
# HONOR CODE:
#   On my honor, as an Aggie, I have neither given nor received
#   unauthorized aid on this academic work.

"""
This file serves as the entry point for the modular personal finance
application.

Modules:
    - operations/database.py:
        Database setup, user authentication, and category initialization
    - operations/finance_operations.py:
        Finance-related CRUD operations and summaries
    - gui/auth.py:
        User login and registration interface
    - gui/expense_pages.py:
        Expense management GUI
    - gui/income_pages.py:
        Income management GUI
    - gui/budget_pages.py:
        Budget overview GUI
    - gui/account_pages.py:
        Account management GUI
    - gui/main_app.py:
        Main application window and navigation
    - analytics/:
        Reporting and analytics modules
    - main.py:
        Application entry point (this file)

Execution:
    Run the application with:
        python main.py
"""

from operations.database import (
    setup_user_db,
    setup_finance_db,
    initialize_expense_categories,
    initialize_income_categories,
)
from gui.auth import AuthWindow
from gui.main_app import MainApp


# ----------------------------------------------------------------------
# Database Initialization
# ----------------------------------------------------------------------
def initialize_databases():
    """
    Initialize all required databases for the application.

    - Creates user and finance databases if not present
    - Initializes default income and expense categories
    """
    setup_user_db()
    setup_finance_db()
    initialize_expense_categories()
    initialize_income_categories()


# ----------------------------------------------------------------------
# Main Application Launcher
# ----------------------------------------------------------------------
def open_main_app(username: str):
    """
    Callback to launch the main application window after authentication.

    Args:
        username (str): The username of the authenticated user.
    """
    app = MainApp(username)
    app.run()


# ----------------------------------------------------------------------
# Entry Point
# ----------------------------------------------------------------------
def main():
    """
    Main application entry point.

    Steps:
        1. Initialize databases
        2. Launch authentication window
        3. Open main app on successful login
    """
    initialize_databases()

    auth_window = AuthWindow(open_main_app)
    auth_window.run()


if __name__ == "__main__":
    main()
