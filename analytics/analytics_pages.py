# PROGRAM: Analytics Pages
# PURPOSE: Provide navigation options for analytics reports including
#          category, monthly, top categories, and cash flow.
# INPUT: Username and parent tkinter frame.
# PROCESS: Display buttons that open the chosen analytics report.
# OUTPUT: Analytics menu with navigation to individual report pages.
# HONOR CODE: On my honor, as an Aggie, I have neither given nor
#             received unauthorized aid on this academic work.

import ttkbootstrap as ttk
from .category import CategoryReport
from .monthly import MonthlyReport
from .top_categories import TopCategoriesReport
from .cash_flow import CashFlowReport


class AnalyticPages:
    """Container for analytics options and report navigation."""

    def __init__(self, username, parent_frame):
        """
        Initialize AnalyticPages.

        Args:
            username (str): Logged-in username.
            parent_frame: Parent tkinter frame for rendering content.
        """
        self.username = username
        self.parent_frame = parent_frame

    # ------------------------------------------------------------------
    # Public
    # ------------------------------------------------------------------
    def create_analytic_page(self):
        """Display the main analytics menu page."""
        self._show_analytic_options()

    # ------------------------------------------------------------------
    # Internals
    # ------------------------------------------------------------------
    def _show_analytic_options(self):
        """Render all available analytics options as buttons."""
        # Clear existing widgets
        for widget in self.parent_frame.winfo_children():
            widget.destroy()

        ttk.Label(
            self.parent_frame,
            text="Select an Analytic Option",
            font=("Helvetica", 12, "bold"),
        ).pack(pady=10)

        frame = ttk.Frame(self.parent_frame, padding=20)
        frame.pack(fill="both", expand=True)

        # Expenses by Category
        ttk.Button(
            frame,
            text="Expenses by Category Report (Pie)",
            bootstyle="info",
            width=30,
            command=lambda: CategoryReport(
                self.parent_frame,
                self.username,
                self._show_analytic_options,
            ).show(),
        ).pack(pady=5)

        # Monthly Expenses
        ttk.Button(
            frame,
            text="Monthly Expenses Report (Bar)",
            bootstyle="info",
            width=30,
            command=lambda: MonthlyReport(
                self.parent_frame,
                self.username,
                self._show_analytic_options,
            ).show(),
        ).pack(pady=5)

        # Top Categories
        ttk.Button(
            frame,
            text="Top Categories (Bar)",
            bootstyle="info",
            width=30,
            command=lambda: TopCategoriesReport(
                self.parent_frame,
                self.username,
                self._show_analytic_options,
            ).show(),
        ).pack(pady=5)

        # Cash Flow
        ttk.Button(
            frame,
            text="Cash Flow (Income vs Expenses)",
            bootstyle="info",
            width=30,
            command=lambda: CashFlowReport(
                self.parent_frame,
                self.username,
                self._show_analytic_options,
            ).show(),
        ).pack(pady=5)

        # --------------------------------------------------------------
        # Close Button
        # --------------------------------------------------------------
        def close_analytics_page():
            """Clear the parent frame to close the analytics page."""
            for widget in self.parent_frame.winfo_children():
                widget.destroy()

        ttk.Button(
            frame,
            text="Close Analytics Page",
            bootstyle="danger",
            width=30,
            command=close_analytics_page,
        ).pack(pady=10)
