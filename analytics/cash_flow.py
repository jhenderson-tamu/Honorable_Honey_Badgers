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
#   - Render a line chart or stacked bar chart with matplotlib.
# OUTPUT:
#   - Tkinter-embedded chart with value labels, shading, and navigation buttons.
# HONOR CODE: On my honor, as an Aggie, I have neither given nor
#             received unauthorized aid on this academic work.

import os
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
from tkinter import filedialog, messagebox
from matplotlib.ticker import FuncFormatter
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import ttkbootstrap as ttk
from ttkbootstrap.widgets import DateEntry
from operations.finance_operations import FinanceOperations
from analytics.helpers import make_action_buttons


class CashFlowReport:
    """Page to display a cash flow chart (Income vs Expenses vs Net)."""

    def __init__(self, parent, username, back_callback):
        """Initialize the cash flow report."""
        self.parent = parent
        self.username = username
        self.back_callback = back_callback
        self.finance_ops = FinanceOperations()
        self._fig = None  # last chart figure (for export)

    def show(self):
        """Render the Cash Flow report page."""
        # Clear frame
        for widget in self.parent.winfo_children():
            widget.destroy()

        # Configure grid weights
        self.parent.grid_rowconfigure(2, weight=1)
        self.parent.grid_columnconfigure(0, weight=1)

        # Title
        ttk.Label(
            self.parent,
            text="Cash Flow (Income vs Expenses vs Net Savings)",
            font=("Helvetica", 14, "bold"),
        ).grid(row=0, column=0, pady=10)

        # Controls
        control_frame = ttk.Frame(self.parent, padding=10)
        control_frame.grid(row=1, column=0, sticky="ew", padx=10, pady=5)

        ttk.Label(control_frame, text="Start Date:").grid(row=0, column=0, sticky="w")
        start_entry = DateEntry(control_frame, bootstyle="info", dateformat="%Y-%m-%d")
        start_entry.set_date(datetime.today().replace(day=1))
        start_entry.grid(row=0, column=1, padx=5)

        ttk.Label(control_frame, text="End Date:").grid(row=0, column=2, sticky="w")
        end_entry = DateEntry(control_frame, bootstyle="info", dateformat="%Y-%m-%d")
        end_entry.set_date(datetime.today())
        end_entry.grid(row=0, column=3, padx=5)

        ttk.Label(control_frame, text="Chart Type:").grid(
            row=0, column=4, padx=(15, 5), sticky="w"
        )
        chart_type_combo = ttk.Combobox(
            control_frame,
            values=["Line Chart", "Stacked Bar Chart"],
            state="readonly",
            width=18,
        )
        chart_type_combo.set("Line Chart")
        chart_type_combo.grid(row=0, column=5, padx=5)

        # Chart container
        chart_frame = ttk.Frame(self.parent, padding=10)
        chart_frame.grid(row=2, column=0, sticky="nsew", padx=10, pady=10)
        chart_frame.grid_rowconfigure(0, weight=1)
        chart_frame.grid_columnconfigure(0, weight=1)

        # Chart builder
        def generate_report(event=None):
            for widget in chart_frame.winfo_children():
                widget.destroy()

            start_date = start_entry.get_date()
            end_date = end_entry.get_date()
            chart_type = chart_type_combo.get()

            # Fetch DB data
            expenses = self.finance_ops.get_user_expenses(self.username)
            income = self.finance_ops.get_user_income(self.username)
            if not expenses and not income:
                ttk.Label(chart_frame, text="No data available").grid()
                return

            # Convert to DataFrames
            df_exp = pd.DataFrame(expenses, columns=["id", "date", "category", "amount", "description"])
            df_inc = pd.DataFrame(income, columns=["id", "date", "category", "amount", "description"])
            for df in [df_exp, df_inc]:
                if not df.empty:
                    df["date"] = pd.to_datetime(df["date"], errors="coerce")
                    df["month"] = df["date"].dt.to_period("M")
            if not df_exp.empty:
                df_exp = df_exp[(df_exp["date"] >= start_date) & (df_exp["date"] <= end_date)]
            if not df_inc.empty:
                df_inc = df_inc[(df_inc["date"] >= start_date) & (df_inc["date"] <= end_date)]

            # Aggregate
            exp_monthly = df_exp.groupby("month")["amount"].sum() if not df_exp.empty else pd.Series(dtype=float)
            inc_monthly = df_inc.groupby("month")["amount"].sum() if not df_inc.empty else pd.Series(dtype=float)
            df = pd.DataFrame({"Expenses": exp_monthly, "Income": inc_monthly}).fillna(0)
            df["Net"] = df["Income"] - df["Expenses"]
            df.index = df.index.to_timestamp()
            df = df.sort_index()
            if df.empty:
                ttk.Label(chart_frame, text="No data in this range").grid()
                return

            # Formatter
            def dollar_formatter(x, _):
                if abs(x) >= 1_000_000:
                    return f"${x/1_000_000:.1f}M"
                elif abs(x) >= 1_000:
                    return f"${x/1_000:.0f}K"
                return f"${x:,.0f}"

            # Plot
            fig, ax = plt.subplots(figsize=(9, 5))
            ax.yaxis.set_major_formatter(FuncFormatter(dollar_formatter))

            if chart_type == "Line Chart":
                ax.plot(df.index, df["Expenses"], marker="o", color="red", label="Expenses")
                ax.plot(df.index, df["Income"], marker="o", color="green", label="Income")
                ax.plot(df.index, df["Net"], marker="o", linestyle="--", color="blue", label="Net Savings")

                # Shading under Net line
                ax.fill_between(df.index, df["Net"], 0, where=(df["Net"] >= 0),
                                interpolate=True, color="green", alpha=0.1)
                ax.fill_between(df.index, df["Net"], 0, where=(df["Net"] < 0),
                                interpolate=True, color="red", alpha=0.1)

                # Dollar labels
                for x, y in zip(df.index, df["Expenses"]):
                    ax.text(x, y, f"${y:,.0f}", ha="center", va="bottom", fontsize=8, color="red")
                for x, y in zip(df.index, df["Income"]):
                    ax.text(x, y, f"${y:,.0f}", ha="center", va="bottom", fontsize=8, color="green")
                for x, y in zip(df.index, df["Net"]):
                    va = "bottom" if y >= 0 else "top"
                    ax.text(x, y, f"${y:,.0f}", ha="center", va=va,
                            fontsize=8, color="blue", fontweight="bold")

            else:  # Stacked Bar Chart
                width = 20
                ax.bar(df.index, df["Income"], width=width, color="green", label="Income")
                ax.bar(df.index, -df["Expenses"], width=width, color="red", label="Expenses")
                ax.plot(df.index, df["Net"], marker="o", linestyle="--", color="blue", label="Net Savings")

                # Dollar labels
                for x, y in zip(df.index, df["Income"]):
                    ax.text(x, y, f"${y:,.0f}", ha="center", va="bottom", fontsize=8, color="green")
                for x, y in zip(df.index, df["Expenses"]):
                    ax.text(x, -y, f"${y:,.0f}", ha="center", va="top", fontsize=8, color="red")
                for x, y in zip(df.index, df["Net"]):
                    va = "bottom" if y >= 0 else "top"
                    ax.text(x, y, f"${y:,.0f}", ha="center", va=va,
                            fontsize=8, color="blue", fontweight="bold")

            # Final formatting
            ax.set_title(f"Cash Flow: {start_date:%b %Y} → {end_date:%b %Y}")
            ax.set_xlabel("Month")
            ax.set_ylabel("Amount (USD)")
            ax.legend()
            ax.grid(True, linestyle="--", alpha=0.7)
            ax.set_xticks(df.index)
            ax.set_xticklabels([d.strftime("%b %Y") for d in df.index], rotation=45, ha="right")
            fig.tight_layout()

            # Save fig for export
            self._fig = fig

            # Embed
            canvas = FigureCanvasTkAgg(fig, master=chart_frame)
            canvas.draw()
            canvas.get_tk_widget().grid(row=0, column=0, sticky="nsew")

        # Export function
        def export_chart():
            if not self._fig:
                return
            filepath = filedialog.asksaveasfilename(
                defaultextension=".png",
                filetypes=[("PNG Image", "*.png")],
                title="Save Cash Flow Report As",
            )
            if filepath:
                try:
                    self._fig.savefig(filepath, dpi=150, bbox_inches="tight", pad_inches=0.2)
                    messagebox.showinfo("Export Successful", f"Chart saved to:\n{os.path.abspath(filepath)}")
                except Exception as error:
                    messagebox.showerror("Export Failed", str(error))

        # Buttons (created once)
        make_action_buttons(
            self.parent,
            [
                ("Export Chart as PNG", export_chart, "info"),
                ("Back", self.back_callback, "danger"),
            ],
            width=25,
            use_grid=True,
        )

        # Bindings
        start_entry.bind("<<DateEntrySelected>>", generate_report)
        end_entry.bind("<<DateEntrySelected>>", generate_report)
        chart_type_combo.bind("<<ComboboxSelected>>", generate_report)

        generate_report()
