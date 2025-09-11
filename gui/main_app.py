# PROGRAM: Main Application Window
# PURPOSE: Create and manage the main application window after a
# successful login, providing navigation to Expenses, Income, Budget,
# Reports, and Account management pages.
# INPUT: Username of the logged-in user.
# PROCESS: Builds a main window with a sidebar for navigation and a
# content frame to display different application pages.
# OUTPUT: GUI interface for managing expenses, income, budgets, and
# account settings.
# HONOR CODE: On my honor, as an Aggie, I have neither given nor
# received unauthorized aid on this academic work.

import ttkbootstrap as ttk
from ttkbootstrap.constants import YES
from operations.database import log_user_action
from gui.expense_pages import ExpensePages
from gui.income_pages import IncomePages
from gui.budget_pages import BudgetPages
from gui.account_pages import AccountPages


class MainApp:
    """Main application class to build and manage the GUI."""

    def __init__(self, username: str):
        """
        Initialize the main application.

        Args:
            username (str): Username of the logged-in user.
        """
        self.username = username
        self.setup_main_window()

    # ------------------------------------------------------------------
    # Window Setup
    # ------------------------------------------------------------------
    def setup_main_window(self):
        """Configure and display the main application window."""
        # Reset style instance before creating the main window
        ttk.Style.instance = None

        # Create and configure main window
        self.main = ttk.Window(themename="solar")
        self.main.title("Main Application")
        self.main.geometry("800x800")

        # Welcome message
        ttk.Label(
            self.main,
            text=f"Welcome, {self.username}!",
            font=("Helvetica", 16, "bold")
        ).pack(pady=10)

        # Main container with sidebar + content frame
        container = ttk.Frame(self.main)
        container.pack(fill="both", expand=YES)

        self.sidebar = ttk.Frame(container, padding=10)
        self.sidebar.pack(side="left", fill="y")

        self.content_frame = ttk.Frame(
            container, padding=10, relief="ridge", borderwidth=2
        )
        self.content_frame.pack(side="right", fill="both", expand=YES)

        # Initialize page objects
        self.expense_pages = ExpensePages(self.username, self.content_frame)
        self.income_pages = IncomePages(self.username, self.content_frame)
        self.budget_pages = BudgetPages(self.username, self.content_frame)
        self.account_pages = AccountPages(self.username, self.content_frame)

        self.setup_sidebar()

    def setup_sidebar(self):
        """Create sidebar navigation buttons."""
        ttk.Button(
            self.sidebar, text="Expenses", bootstyle="primary",
            command=self.show_expenses
        ).pack(fill="x", pady=5)

        ttk.Button(
            self.sidebar, text="Income", bootstyle="primary",
            command=self.show_income
        ).pack(fill="x", pady=5)

        ttk.Button(
            self.sidebar, text="Budget", bootstyle="primary",
            command=self.show_budget
        ).pack(fill="x", pady=5)

        ttk.Button(
            self.sidebar, text="Reports", bootstyle="primary",
            command=self.show_reports
        ).pack(fill="x", pady=5)

        ttk.Button(
            self.sidebar, text="Manage Account", bootstyle="primary",
            command=self.show_account
        ).pack(fill="x", pady=5)

        ttk.Button(
            self.sidebar, text="Logout", bootstyle="danger",
            command=self.logout
        ).pack(fill="x", pady=20)

    # ------------------------------------------------------------------
    # Page Display Methods
    # ------------------------------------------------------------------
    def clear_content_frame(self):
        """Clear all widgets from the content frame."""
        for widget in self.content_frame.winfo_children():
            widget.destroy()

    def show_expenses(self):
        """Display the expenses page."""
        self.clear_content_frame()
        self.expense_pages.create_expenses_page()

    def show_income(self):
        """Display the income page."""
        self.clear_content_frame()
        self.income_pages.create_income_page()

    def show_budget(self):
        """Display the budget page."""
        self.clear_content_frame()
        self.budget_pages.create_budget_page()

    def show_reports(self):
        """Display the reports page (currently placeholder)."""
        self.clear_content_frame()
        ttk.Label(
            self.content_frame,
            text="Reports Page - Coming Soon!",
            font=("Helvetica", 14)
        ).pack(pady=20)

    def show_account(self):
        """Display the account management page."""
        self.clear_content_frame()
        self.account_pages.create_management_page()

    def logout(self):
        """Log the user out and close the application."""
        log_user_action(self.username, "Logout")
        self.main.destroy()

    # ------------------------------------------------------------------
    # Main Loop
    # ------------------------------------------------------------------
    def run(self):
        """Run the main application event loop."""
        self.main.mainloop()
