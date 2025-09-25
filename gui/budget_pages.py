# PROGRAM: Budget Overview Pages
# PURPOSE: Display a budget overview for a given date range, showing
#          total expenses, total income, and remaining savings.
# INPUT:
#   - username (str): Username of the logged-in user.
#   - parent_frame (tk.Frame): The parent container where the budget
#     overview page will be rendered.
# PROCESS:
#   - Collects user-selected date range via DateEntry widgets.
#   - Retrieves expense and income data from FinanceOperations.
#   - Calculates totals, net savings, and savings transfers.
#   - Updates GUI labels dynamically when the date range changes.
# OUTPUT:
#   - Total expenses, income, net savings, and savings transfers
#     displayed on screen within the budget overview page.
# HONOR CODE: On my honor, as an Aggie, I have neither given nor
#             received unauthorized aid on this academic work.

import tkinter as tk
import ttkbootstrap as ttk
from ttkbootstrap.constants import YES
from datetime import datetime
from operations.finance_operations import FinanceOperations


class BudgetPages:
    """Class responsible for creating and managing budget overview pages."""

    def __init__(self, username: str, parent_frame):
        """
        Initialize the BudgetPages instance.

        Args:
            username (str): Username of the logged-in user.
            parent_frame (tk.Frame): The frame where budget pages will be displayed.
        """
        self.username = username
        self.parent_frame = parent_frame
        self.finance_ops = FinanceOperations()

    # ------------------------------------------------------------------
    # Page Builder
    # ------------------------------------------------------------------
    def create_budget_page(self):
        """
        Build and display the budget overview page.

        Features:
            - Start and End date pickers to filter the budget period.
            - Dynamic calculation of total expenses, total income,
              net savings, and savings transfers.
            - Auto-updates values when dates are changed.
            - Close button to exit back to the main menu.
        """
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
        start_entry.set_date(datetime.today().replace(day=1))  # Default = first of month
        start_entry.pack(fill="x", pady=5)

        ttk.Label(frame, text="End Date (YYYY-MM-DD):").pack(anchor="w")
        end_entry = ttk.DateEntry(
            frame, bootstyle="info", dateformat="%Y-%m-%d"
        )
        end_entry.set_date(datetime.today())  # Default = today
        end_entry.pack(fill="x", pady=5)

        # --- Result Variables and Labels ---
        expense_var = tk.StringVar(value="Total Expenses: $0.00")
        income_var = tk.StringVar(value="Total Income: $0.00")
        leftover_var = tk.StringVar(value="Net Savings: $0.00")
        savings_var = tk.StringVar(value="Savings Transfers: $0.00")

        ttk.Label(frame, textvariable=expense_var, font=("Helvetica", 12)).pack(anchor="w", pady=5)
        ttk.Label(frame, textvariable=income_var, font=("Helvetica", 12)).pack(anchor="w", pady=5)
        ttk.Label(frame, textvariable=leftover_var, font=("Helvetica", 12, "bold")).pack(anchor="w", pady=10)
        ttk.Label(frame, textvariable=savings_var, font=("Helvetica", 12)).pack(anchor="w", pady=5)

        # ------------------------------------------------------------------
        # Budget Calculation Function
        # ------------------------------------------------------------------
        def update_budget(*args):
            """
            Update the budget summary values based on the selected date range.

            Workflow:
                - Get selected start and end dates.
                - Call FinanceOperations.get_budget_summary() to fetch:
                    total_expenses, total_income, net_savings, savings_transfers.
                - Update all corresponding StringVars to refresh labels.
            """
            start_date = start_entry.get_date().strftime("%Y-%m-%d")
            end_date = end_entry.get_date().strftime("%Y-%m-%d")

            total_expenses, total_income, net_savings, savings_transfers = self.finance_ops.get_budget_summary(
                self.username, start_date, end_date
            )

            expense_var.set(f"Total Expenses: ${total_expenses:,.2f}")
            income_var.set(f"Total Income: ${total_income:,.2f}")
            leftover_var.set(f"Net Savings: ${net_savings:,.2f}")
            savings_var.set(f"Savings Transfers: ${savings_transfers:,.2f}")

        # Auto-update when dates change
        start_entry.bind("<<DateEntrySelected>>", update_budget)
        end_entry.bind("<<DateEntrySelected>>", update_budget)

        # Run once on load
        update_budget()

        # ------------------------------------------------------------------
        # Close Button
        # ------------------------------------------------------------------
        def back_to_main():
            """Clear the frame and return to the main menu."""
            for widget in self.parent_frame.winfo_children():
                widget.destroy()

        ttk.Button(
            frame, text="Close Budget Page", bootstyle="danger",
            command=back_to_main
        ).pack(pady=10)
