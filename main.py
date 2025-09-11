
"""
Personal Finance Application - Modular Version

This is the main entry point for the personal finance application.
The application has been modularized into several files:

- database.py: Database setup and operations
- finance_operations.py: Finance data operations
- auth.py: Authentication GUI
- expense_pages.py: Expense management GUI
- income_pages.py: Income management GUI
- budget_pages.py: Budget management GUI
- account_pages.py: Account management GUI
- main_app.py: Main application GUI
- main.py: Application entry point (this file)

To run the application, execute: python main.py
"""

from operations.database import setup_user_db, setup_finance_db, \
    initialize_expense_categories, initialize_income_categories
from gui.auth import AuthWindow
from gui.main_app import MainApp

def initialize_databases():
    """Initialize all required databases"""
    setup_user_db()
    setup_finance_db()
    initialize_expense_categories()
    initialize_income_categories()

def open_main_app(username):
    """Callback function to open main app after successful login"""
    main_app = MainApp(username)
    main_app.run()

def main():
    """Main application entry point"""
    # Initialize databases
    initialize_databases()

    # Start with authentication window
    auth_window = AuthWindow(open_main_app)
    auth_window.run()

if __name__ == "__main__":
    main()