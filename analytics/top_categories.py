# PROGRAM: Top Categories Report with Date Range, Auto-Update, and USD Labels
# PURPOSE: Display top expense categories ranked by spending, filtered by date
# INPUT: Username, parent frame, back callback
# PROCESS: Query all expenses, filter with pandas, group by category, sum, plot top N
# OUTPUT: Horizontal bar chart with USD labels and bar amounts

import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import ttkbootstrap as ttk
from ttkbootstrap.widgets import DateEntry
import pandas as pd
from datetime import datetime
from operations.finance_operations import FinanceOperations


class TopCategoriesReport:
    def __init__(self, parent, username, back_callback):
        self.parent = parent
        self.username = username
        self.back_callback = back_callback
        self.finance_ops = FinanceOperations()

    def show(self):
        # Clear parent frame
        for w in self.parent.winfo_children():
            w.destroy()

        ttk.Label(
            self.parent, text="Top Spending Categories",
            font=("Helvetica", 14, "bold")
        ).pack(pady=10)

        # --- Date Pickers ---
        date_frame = ttk.Frame(self.parent, padding=10)
        date_frame.pack(fill="x")

        ttk.Label(date_frame, text="Start Date:").grid(row=0, column=0, sticky="w")
        start_entry = DateEntry(date_frame, bootstyle="info", dateformat="%Y-%m-%d")
        start_entry.set_date(datetime.today().replace(day=1))  # default = first of month
        start_entry.grid(row=0, column=1, padx=5)

        ttk.Label(date_frame, text="End Date:").grid(row=0, column=2, sticky="w")
        end_entry = DateEntry(date_frame, bootstyle="info", dateformat="%Y-%m-%d")
        end_entry.set_date(datetime.today())  # default = today
        end_entry.grid(row=0, column=3, padx=5)

        # Frame to hold the chart
        chart_frame = ttk.Frame(self.parent, padding=10)
        chart_frame.pack(fill="both", expand=True)

        # --- Chart Generator ---
        def generate_report(*args):
            for w in chart_frame.winfo_children():
                w.destroy()

            start_date = start_entry.get_date()
            end_date = end_entry.get_date()

            # Fetch all user expenses
            expenses = self.finance_ops.get_user_expenses(self.username)
            if not expenses:
                ttk.Label(chart_frame, text="No expenses available").pack(pady=10)
                return

            # Convert to DataFrame
            df = pd.DataFrame(expenses, columns=["id", "date", "category", "amount", "description"])
            df["date"] = pd.to_datetime(df["date"], errors="coerce")

            # Filter by selected range
            mask = (df["date"] >= pd.to_datetime(start_date)) & (df["date"] <= pd.to_datetime(end_date))
            df = df.loc[mask]

            if df.empty:
                ttk.Label(chart_frame, text="No expenses in this date range").pack(pady=10)
                return

            # Group, sort, top 10
            df = df.groupby("category")["amount"].sum().reset_index()
            df = df.sort_values("amount", ascending=False).head(10)

            # --- Dynamic chart sizing ---
            n = len(df)
            fig, ax = plt.subplots(figsize=(8, max(4, 0.5 * n)))

            bars = ax.barh(df["category"], df["amount"], color="#4a90e2")

            ax.set_xlabel("Amount (USD)")
            ax.set_ylabel("Category")
            ax.set_title(f"Top Categories: {start_date:%Y-%m-%d} → {end_date:%Y-%m-%d}")
            ax.invert_yaxis()

            # Add labels with amounts on bars
            for bar, amount in zip(bars, df["amount"]):
                ax.text(
                    bar.get_width() + (0.01 * max(df["amount"])),  # a little to the right
                    bar.get_y() + bar.get_height() / 2,
                    f"${amount:,.2f}",
                    va="center",
                    ha="left",
                    fontsize=9,
                    color="black"
                )

            # Fit labels
            ax.tick_params(axis="y", labelsize=9)
            fig.tight_layout()

            # Embed into Tkinter
            canvas = FigureCanvasTkAgg(fig, master=chart_frame)
            canvas.draw()
            canvas.get_tk_widget().pack(pady=10, fill="both", expand=True)

        # --- Bind auto-update to date pickers ---
        start_entry.bind("<<DateEntrySelected>>", generate_report)
        end_entry.bind("<<DateEntrySelected>>", generate_report)

        # Draw chart on load
        generate_report()

        # Back button
        ttk.Button(
            self.parent, text="Back", bootstyle="danger",
            command=self.back_callback
        ).pack(pady=5)
