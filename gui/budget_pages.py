# PROGRAM: Budget Overview Pages
# PURPOSE: Display a budget overview for a given date range, showing
# total expenses, total income, and remaining savings.
# INPUT: Username of the logged-in user and a parent frame for display.
# PROCESS: Collects user-selected date range, retrieves data from
# FinanceOperations, calculates totals, and updates GUI.
# OUTPUT: Total expenses, income, and leftover savings shown on screen.
# HONOR CODE: On my honor, as an Aggie, I have neither given nor
# received unauthorized aid on this academic work.

import tkinter as tk
import ttkbootstrap as ttk
from ttkbootstrap.constants import YES
from datetime import datetime
from operations.finance_operations import FinanceOperations


class BudgetPages:
    """Class responsible for creating and managing budget pages."""

    def __init__(self, username: str, parent_frame):
        """
        Initialize BudgetPages instance.

        Args:
            username (str): Username of the logged-in user.
            parent_frame: The frame where budget pages will be displayed.
        """
        self.username = username
        self.parent_frame = parent_frame
        self.finance_ops = FinanceOperations()

    def create_budget_page(self):
        """Create and display the budget overview page."""
        # Clear existing widgets
        for widget in self.parent_frame.winfo_children():
            widget.destroy()

        # Page title
        ttk.Label(
            self.parent_frame,
            text=f"Budget Overview for {self.username}",
            font=("Helvetica", 14, "bold")
        ).pack(pady=15)

        frame = ttk.Frame(self.parent_frame, padding=20)
        frame.pack(fill="both", expand=YES)

        # --- Date Range Inputs ---
        ttk.Label(frame, text="Start Date (YYYY-MM-DD):").pack(anchor="w")
        start_entry = ttk.DateEntry(
            frame, bootstyle="info", dateformat="%Y-%m-%d"
        )
        start_entry.set_date(datetime.today().replace(day=1))  # First of month
        start_entry.pack(fill="x", pady=5)

        ttk.Label(frame, text="End Date (YYYY-MM-DD):").pack(anchor="w")
        end_entry = ttk.DateEntry(
            frame, bootstyle="info", dateformat="%Y-%m-%d"
        )
        end_entry.set_date(datetime.today())  # Today
        end_entry.pack(fill="x", pady=5)

        # --- Result Variables and Labels ---
        expense_var = tk.StringVar(value="Total Expenses: $0.00")
        income_var = tk.StringVar(value="Total Income: $0.00")
        leftover_var = tk.StringVar(value="Total Savings: $0.00")

        ttk.Label(
            frame, textvariable=expense_var, font=("Helvetica", 12)
        ).pack(anchor="w", pady=5)
        ttk.Label(
            frame, textvariable=income_var, font=("Helvetica", 12)
        ).pack(anchor="w", pady=5)
        ttk.Label(
            frame, textvariable=leftover_var, font=("Helvetica", 12, "bold")
        ).pack(anchor="w", pady=10)

        def calculate_budget():
            """
            Calculate and update budget summary for the selected date range.
            """
            start_date = start_entry.get_date().strftime("%Y-%m-%d")
            end_date = end_entry.get_date().strftime("%Y-%m-%d")

            total_expenses, total_income, leftover = self.finance_ops.get_budget_summary(
                self.username, start_date, end_date
            )

            # Update UI labels
            expense_var.set(f"Total Expenses: ${total_expenses:,.2f}")
            income_var.set(f"Total Income: ${total_income:,.2f}")
            leftover_var.set(f"Total Savings: ${leftover:,.2f}")

        # --- Buttons ---
        ttk.Button(
            frame, text="Calculate Budget", bootstyle="success",
            command=calculate_budget
        ).pack(pady=15)

        def back_to_main():
            """Clear the parent frame and return to main menu."""
            for widget in self.parent_frame.winfo_children():
                widget.destroy()

        ttk.Button(
            frame, text="Close Budget Page", bootstyle="danger",
            command=back_to_main
        ).pack(pady=10)
