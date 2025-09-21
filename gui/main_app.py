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
from analytics.analytics_pages import AnalyticPages

class MainApp:
    """Main application class to build and manage the GUI."""

    def __init__(self, username: str):
        """
        Initialize the main application.

        Args:
            username (str): Username of the logged-in user.
        """
        self.username = username
        self._setup_main_window()

    # ------------------------------------------------------------------
    # Window Setup
    # ------------------------------------------------------------------
    def _setup_main_window(self):
        """Configure and display the main application window."""
        # Reset style instance before creating the main window
        ttk.Style.instance = None

        # Create and configure main window
        self.main = ttk.Window(themename="solar")
        self.main.title("Main Application")
        self.main.geometry("850x800")

        # Welcome message
        ttk.Label(
            self.main,
            text=f"Welcome, {self.username}!",
            font=("Helvetica", 16, "bold")
        ).pack(pady=10)

        # Main container with sidebar + content frame
        container = ttk.Frame(self.main)
        container.pack(fill="both", expand=YES)

        # Sidebar
        self.sidebar = ttk.Frame(container, padding=10)
        self.sidebar.pack(side="left", fill="y")

        # Content frame
        self.content_frame = ttk.Frame(
            container, padding=10, relief="ridge", borderwidth=2
        )
        self.content_frame.pack(side="right", fill="both", expand=YES)

        # Initialize page objects
        self.expense_pages = ExpensePages(self.username, self.content_frame)
        self.income_pages = IncomePages(self.username, self.content_frame)
        self.budget_pages = BudgetPages(self.username, self.content_frame)
        self.account_pages = AccountPages(self.username, self.content_frame)
        self.analytic_pages = AnalyticPages(self.username, self.content_frame)

        # Build sidebar navigation
        self._setup_sidebar()

    def _setup_sidebar(self):
        """Create sidebar navigation buttons."""
        menu_items = [
            ("Expenses", self.show_expenses),
            ("Income", self.show_income),
            ("Budget", self.show_budget),
            ("Analytics", self.show_analytics),
            ("Manage Account", self.show_account),
        ]

        for text, command in menu_items:
            ttk.Button(
                self.sidebar,
                text=text,
                bootstyle="primary",
                command=command
            ).pack(fill="x", pady=5)

        # Logout button
        ttk.Button(
            self.sidebar,
            text="Logout",
            bootstyle="danger",
            command=self.logout
        ).pack(fill="x", pady=20)

    # ------------------------------------------------------------------
    # Page Display Methods
    # ------------------------------------------------------------------
    def _clear_content_frame(self):
        """Clear all widgets from the content frame."""
        for widget in self.content_frame.winfo_children():
            widget.destroy()

    def show_expenses(self):
        """Display the expenses page."""
        self._clear_content_frame()
        self.expense_pages.create_expenses_page()

    def show_income(self):
        """Display the income page."""
        self._clear_content_frame()
        self.income_pages.create_income_page()

    def show_budget(self):
        """Display the budget page."""
        self._clear_content_frame()
        self.budget_pages.create_budget_page()

    def show_analytics(self):
        """Display the analytics page."""
        self._clear_content_frame()
        self.analytic_pages.create_analytic_page()

    def show_account(self):
        """Display the account management page."""
        self._clear_content_frame()
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
