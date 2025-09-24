# PROGRAM: Cash Flow Report
# PURPOSE: Show Income, Expenses, and Net Savings across months
# INPUT: Username, parent frame, back callback
# PROCESS: Pull expenses and income, group by month, compute net, plot line chart
# OUTPUT: Line chart of monthly income, expenses, and net savings (positive=green, negative=red)

import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import ttkbootstrap as ttk
from ttkbootstrap.widgets import DateEntry
import pandas as pd
from datetime import datetime
from operations.finance_operations import FinanceOperations


class CashFlowReport:
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
            self.parent, text="Cash Flow (Income vs Expenses vs Net Savings)",
            font=("Helvetica", 14, "bold")
        ).pack(pady=10)

        # --- Date Pickers ---
        date_frame = ttk.Frame(self.parent, padding=10)
        date_frame.pack(fill="x")

        ttk.Label(date_frame, text="Start Date:").grid(row=0, column=0, sticky="w")
        start_entry = DateEntry(date_frame, bootstyle="info", dateformat="%Y-%m-%d")
        start_entry.set_date(datetime.today().replace(day=1))
        start_entry.grid(row=0, column=1, padx=5)

        ttk.Label(date_frame, text="End Date:").grid(row=0, column=2, sticky="w")
        end_entry = DateEntry(date_frame, bootstyle="info", dateformat="%Y-%m-%d")
        end_entry.set_date(datetime.today())
        end_entry.grid(row=0, column=3, padx=5)

        chart_frame = ttk.Frame(self.parent, padding=10)
        chart_frame.pack(fill="both", expand=True)

        # --- Chart Generator ---
        def generate_report(*args):
            for w in chart_frame.winfo_children():
                w.destroy()

            start_date = start_entry.get_date()
            end_date = end_entry.get_date()

            # Fetch expenses & income
            expenses = self.finance_ops.get_user_expenses(self.username)
            income = self.finance_ops.get_user_income(self.username)

            if not expenses and not income:
                ttk.Label(chart_frame, text="No data available").pack(pady=10)
                return

            # Convert to DataFrames
            df_exp = pd.DataFrame(expenses, columns=["id", "date", "category", "amount", "description"])
            df_inc = pd.DataFrame(income, columns=["id", "date", "category", "amount", "description"])

            for df in [df_exp, df_inc]:
                if not df.empty:
                    df["date"] = pd.to_datetime(df["date"], errors="coerce")
                    df["month"] = df["date"].dt.to_period("M")

            # Filter by date
            if not df_exp.empty:
                df_exp = df_exp[(df_exp["date"] >= start_date) & (df_exp["date"] <= end_date)]
            if not df_inc.empty:
                df_inc = df_inc[(df_inc["date"] >= start_date) & (df_inc["date"] <= end_date)]

            # Group by month
            exp_monthly = df_exp.groupby("month")["amount"].sum() if not df_exp.empty else pd.Series(dtype=float)
            inc_monthly = df_inc.groupby("month")["amount"].sum() if not df_inc.empty else pd.Series(dtype=float)

            # Combine into one DataFrame
            df = pd.DataFrame({"Expenses": exp_monthly, "Income": inc_monthly}).fillna(0)
            df["Net"] = df["Income"] - df["Expenses"]   # ✅ Net Savings
            df.index = df.index.to_timestamp()
            df = df.sort_index()

            if df.empty:
                ttk.Label(chart_frame, text="No data in this range").pack(pady=10)
                return

            # --- Plot ---
            fig, ax = plt.subplots(figsize=(8, 5))
            ax.plot(df.index, df["Expenses"], marker="o", color="red", label="Expenses")
            ax.plot(df.index, df["Income"], marker="o", color="green", label="Income")
            ax.plot(df.index, df["Net"], marker="o", color="blue", linestyle="--", label="Net Savings")

            # Overlay colored dots for Net (green=positive, red=negative)
            for x, y in zip(df.index, df["Net"]):
                ax.scatter(x, y, color="green" if y >= 0 else "red", zorder=5)

            ax.set_xlabel("Month")
            ax.set_ylabel("Amount (USD)")
            ax.set_title(f"Cash Flow: {start_date:%Y-%m-%d} → {end_date:%Y-%m-%d}")
            ax.legend()
            ax.grid(True, linestyle="--", alpha=0.6)

            # Rotate x-axis labels vertically
            plt.setp(ax.get_xticklabels(), rotation=90, ha="center")

            # --- Add value labels ---
            for x, y in zip(df.index, df["Expenses"]):
                ax.text(x, y + (0.01 * df["Expenses"].max()), f"${y:,.2f}",
                        ha="center", va="bottom", fontsize=8, color="red")

            for x, y in zip(df.index, df["Income"]):
                ax.text(x, y + (0.01 * df["Income"].max()), f"${y:,.2f}",
                        ha="center", va="bottom", fontsize=8, color="green")

            for x, y in zip(df.index, df["Net"]):
                ax.text(x, y + (0.01 * max(abs(df["Net"].max()), abs(df["Net"].min()))),
                        f"${y:,.2f}", ha="center", va="bottom",
                        fontsize=8, color="green" if y >= 0 else "red")

            fig.tight_layout()

            canvas = FigureCanvasTkAgg(fig, master=chart_frame)
            canvas.draw()
            canvas.get_tk_widget().pack(pady=10, fill="both", expand=True)

        # Bind date pickers to auto-update
        start_entry.bind("<<DateEntrySelected>>", generate_report)
        end_entry.bind("<<DateEntrySelected>>", generate_report)

        # Draw chart on load
        generate_report()

        # Back button
        ttk.Button(
            self.parent, text="Back", bootstyle="danger",
            command=self.back_callback
        ).pack(pady=5)
