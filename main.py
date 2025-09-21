# PROGRAM: Personal Finance Application - Modular Version
# PURPOSE: This is the main entry point for the personal finance application.
# INPUT: User login credentials and financial data inputs (expenses, income, budgets).
# PROCESS: Initialize required databases, authenticate the user, and launch the GUI.
# OUTPUT: Graphical interface for managing personal finance data.
# HONOR CODE: On my honor, as an Aggie, I have neither given nor
# received unauthorized aid on this academic work.

"""
This program serves as the entry point for the modular personal finance application.

Modules:
    - operations/database.py: Database setup and operations
    - operations/finance_operations.py: Finance data operations
    - gui/auth.py: Authentication GUI
    - gui/expense_pages.py: Expense management GUI
    - gui/income_pages.py: Income management GUI
    - gui/budget_pages.py: Budget management GUI
    - gui/account_pages.py: Account management GUI
    - gui/main_app.py: Main application GUI (post-login)
    - analytics/: Reporting and analytics module
    - main.py: Application entry point (this file)

Execution:
    To run the application, execute:
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
    """Initialize all required databases for the application."""
    setup_user_db()
    setup_finance_db()
    initialize_expense_categories()
    initialize_income_categories()


# ----------------------------------------------------------------------
# Main Application Launcher
# ----------------------------------------------------------------------
def open_main_app(username: str):
    """
    Callback function to open the main application window
    after successful authentication.

    Args:
        username (str): The username of the authenticated user.
    """
    app = MainApp(username)
    app.run()


# ----------------------------------------------------------------------
# Entry Point
# ----------------------------------------------------------------------
def main():
    """Main application entry point."""
    # Step 1: Initialize required databases
    initialize_databases()

    # Step 2: Start authentication process
    auth_window = AuthWindow(open_main_app)
    auth_window.run()


if __name__ == "__main__":
    main()
