# PROGRAM: Cash Flow Report
# PURPOSE: Visualize monthly Income, Expenses, and Net Savings for a user.
# INPUT:
#   - username (str): Logged-in user whose data will be queried.
#   - parent (Frame): Parent tkinter frame for rendering the chart UI.
#   - back_callback (function): Callback to return to the previous page.
# PROCESS:
#   - Retrieve income and expense records from SQLite via FinanceOperations.
#   - Convert to pandas DataFrames, filter by date range, and group by month.
#   - Compute net savings (Income - Expenses).
#   - Render a line chart with matplotlib showing Income, Expenses, and Net.
# OUTPUT:
#   - Tkinter-embedded chart with value labels and a back navigation button.
# HONOR CODE: On my honor, as an Aggie, I have neither given nor
#             received unauthorized aid on this academic work.

import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import ttkbootstrap as ttk
from ttkbootstrap.widgets import DateEntry
import pandas as pd
from datetime import datetime
from operations.finance_operations import FinanceOperations


class CashFlowReport:
    """Page to display a cash flow line chart (Income vs Expenses vs Net)."""

    def __init__(self, parent, username, back_callback):
        """
        Initialize the cash flow report.

        Args:
            parent: Tkinter parent frame.
            username (str): Logged-in user to fetch data for.
            back_callback (function): Callback to navigate back.
        """
        self.parent = parent
        self.username = username
        self.back_callback = back_callback
        self.finance_ops = FinanceOperations()

    def show(self):
        """Render the Cash Flow report page."""
        # --------------------------------------------------------------
        # Clear the parent frame
        # --------------------------------------------------------------
        for widget in self.parent.winfo_children():
            widget.destroy()

        ttk.Label(
            self.parent,
            text="Cash Flow (Income vs Expenses vs Net Savings)",
            font=("Helvetica", 14, "bold"),
        ).pack(pady=10)

        # --------------------------------------------------------------
        # Date Pickers
        # --------------------------------------------------------------
        date_frame = ttk.Frame(self.parent, padding=10)
        date_frame.pack(fill="x")

        ttk.Label(date_frame, text="Start Date:").grid(row=0, column=0, sticky="w")
        start_entry = DateEntry(date_frame, bootstyle="info", dateformat="%Y-%m-%d")
        start_entry.set_date(datetime.today().replace(day=1))  # First day of month
        start_entry.grid(row=0, column=1, padx=5)

        ttk.Label(date_frame, text="End Date:").grid(row=0, column=2, sticky="w")
        end_entry = DateEntry(date_frame, bootstyle="info", dateformat="%Y-%m-%d")
        end_entry.set_date(datetime.today())  # Default = today
        end_entry.grid(row=0, column=3, padx=5)

        chart_frame = ttk.Frame(self.parent, padding=10)
        chart_frame.pack(fill="both", expand=True)

        # --------------------------------------------------------------
        # Chart Generator
        # --------------------------------------------------------------
        def generate_report(*args):
            """Build and display the cash flow line chart."""
            # Clear chart frame
            for widget in chart_frame.winfo_children():
                widget.destroy()

            start_date = start_entry.get_date()
            end_date = end_entry.get_date()

            # Fetch expenses & income from DB
            expenses = self.finance_ops.get_user_expenses(self.username)
            income = self.finance_ops.get_user_income(self.username)

            if not expenses and not income:
                ttk.Label(chart_frame, text="No data available").pack(pady=10)
                return

            # Convert results to DataFrames
            df_exp = pd.DataFrame(
                expenses, columns=["id", "date", "category", "amount", "description"]
            )
            df_inc = pd.DataFrame(
                income, columns=["id", "date", "category", "amount", "description"]
            )

            # Normalize dates and extract months
            for df in [df_exp, df_inc]:
                if not df.empty:
                    df["date"] = pd.to_datetime(df["date"], errors="coerce")
                    df["month"] = df["date"].dt.to_period("M")

            # Filter by date range
            if not df_exp.empty:
                df_exp = df_exp[
                    (df_exp["date"] >= start_date) & (df_exp["date"] <= end_date)
                ]
            if not df_inc.empty:
                df_inc = df_inc[
                    (df_inc["date"] >= start_date) & (df_inc["date"] <= end_date)
                ]

            # Group by month
            exp_monthly = (
                df_exp.groupby("month")["amount"].sum()
                if not df_exp.empty else pd.Series(dtype=float)
            )
            inc_monthly = (
                df_inc.groupby("month")["amount"].sum()
                if not df_inc.empty else pd.Series(dtype=float)
            )

            # Merge into single DataFrame
            df = pd.DataFrame({"Expenses": exp_monthly, "Income": inc_monthly}).fillna(0)
            df["Net"] = df["Income"] - df["Expenses"]
            df.index = df.index.to_timestamp()
            df = df.sort_index()

            if df.empty:
                ttk.Label(chart_frame, text="No data in this range").pack(pady=10)
                return

            # ----------------------------------------------------------
            # Plot chart
            # ----------------------------------------------------------
            fig, ax = plt.subplots(figsize=(8, 5))
            ax.plot(df.index, df["Expenses"], marker="o", color="red", label="Expenses")
            ax.plot(df.index, df["Income"], marker="o", color="green", label="Income")
            ax.plot(
                df.index, df["Net"],
                marker="o", color="blue", linestyle="--", label="Net Savings"
            )

            # Colored dots for Net Savings (green = positive, red = negative)
            for x, y in zip(df.index, df["Net"]):
                ax.scatter(x, y, color="green" if y >= 0 else "red", zorder=5)

            ax.set_xlabel("Month")
            ax.set_ylabel("Amount (USD)")
            ax.set_title(f"Cash Flow: {start_date:%Y-%m-%d} → {end_date:%Y-%m-%d}")
            ax.legend()
            ax.grid(True, linestyle="--", alpha=0.6)

            # Rotate x-axis labels vertically
            plt.setp(ax.get_xticklabels(), rotation=90, ha="center")

            # Value labels above points
            for x, y in zip(df.index, df["Expenses"]):
                ax.text(x, y + (0.01 * df["Expenses"].max()), f"${y:,.2f}",
                        ha="center", va="bottom", fontsize=8, color="red")
            for x, y in zip(df.index, df["Income"]):
                ax.text(x, y + (0.01 * df["Income"].max()), f"${y:,.2f}",
                        ha="center", va="bottom", fontsize=8, color="green")
            for x, y in zip(df.index, df["Net"]):
                ax.text(
                    x,
                    y + (0.01 * max(abs(df["Net"].max()), abs(df["Net"].min()))),
                    f"${y:,.2f}",
                    ha="center", va="bottom", fontsize=8,
                    color="green" if y >= 0 else "red",
                )

            fig.tight_layout()

            # Embed chart into Tkinter
            canvas = FigureCanvasTkAgg(fig, master=chart_frame)
            canvas.draw()
            canvas.get_tk_widget().pack(pady=10, fill="both", expand=True)

        # --------------------------------------------------------------
        # Bind events & render on load
        # --------------------------------------------------------------
        start_entry.bind("<<DateEntrySelected>>", generate_report)
        end_entry.bind("<<DateEntrySelected>>", generate_report)
        generate_report()

        # Back button
        ttk.Button(
            self.parent, text="Back",
            bootstyle="danger", command=self.back_callback
        ).pack(pady=5)
