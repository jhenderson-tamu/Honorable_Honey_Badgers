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
#   - Tkinter-embedded chart with value labels and a back navigation button.
# HONOR CODE: On my honor, as an Aggie, I have neither given nor
#             received unauthorized aid on this academic work.

import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import ttkbootstrap as ttk
from ttkbootstrap.widgets import DateEntry
import pandas as pd
from datetime import datetime
from tkinter import filedialog, messagebox
import os
from matplotlib.ticker import FuncFormatter
from operations.finance_operations import FinanceOperations


class CashFlowReport:
    """Page to display a cash flow chart (Income vs Expenses vs Net)."""

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
        # Date Pickers + Chart Type Selector
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

        # Chart type selector
        ttk.Label(date_frame, text="Chart Type:").grid(
            row=0, column=4, padx=(15, 5), sticky="w"
        )
        self.chart_type_combo = ttk.Combobox(
            date_frame,
            values=["Line Chart", "Stacked Bar Chart"],
            state="readonly",
            width=18,
        )
        self.chart_type_combo.set("Line Chart")  # default
        self.chart_type_combo.grid(row=0, column=5, padx=5)

        # Chart container
        chart_frame = ttk.Frame(self.parent, padding=10)
        chart_frame.pack(fill="both", expand=True)

        # --------------------------------------------------------------
        # Chart Generator
        # --------------------------------------------------------------
        def generate_report(*args):
            """Build and display the cash flow chart (line or stacked bar)."""
            # Clear chart frame
            for widget in chart_frame.winfo_children():
                widget.destroy()

            start_date = start_entry.get_date()
            end_date = end_entry.get_date()
            chart_type = self.chart_type_combo.get()

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

            # Helper for currency formatting
            def format_currency(value):
                if abs(value) >= 1_000_000:
                    return f"${value/1_000_000:.2f}M"
                elif abs(value) >= 1_000:
                    return f"${value/1_000:.0f}K"
                return f"${value:.2f}"

            # ----------------------------------------------------------
            # Plot chart
            # ----------------------------------------------------------
            fig, ax = plt.subplots(figsize=(9, 5))
            ax.set_facecolor("#f9f9f9")

            # Format Y-axis as dollars
            def dollar_formatter(x, pos):
                if abs(x) >= 1_000_000:
                    return f"${x/1_000_000:.1f}M"
                elif abs(x) >= 1_000:
                    return f"${x/1_000:.0f}K"
                return f"${x:,.0f}"

            ax.yaxis.set_major_formatter(FuncFormatter(dollar_formatter))

            if chart_type == "Line Chart":
                # 📈 Line Chart
                ax.plot(df.index, df["Expenses"], marker="o", markersize=6,
                        linewidth=2, color="red", label="Expenses")
                ax.plot(df.index, df["Income"], marker="o", markersize=6,
                        linewidth=2, color="green", label="Income")
                ax.plot(df.index, df["Net"], marker="o", markersize=6,
                        linewidth=2, linestyle="--", color="blue", label="Net Savings")

                # Colored dots for Net
                for x, y in zip(df.index, df["Net"]):
                    ax.scatter(x, y, color="green" if y >= 0 else "red", zorder=5)

                # Shaded areas for Net
                ax.fill_between(df.index, df["Net"], 0,
                                where=(df["Net"] >= 0),
                                interpolate=True, color="green", alpha=0.1)
                ax.fill_between(df.index, df["Net"], 0,
                                where=(df["Net"] < 0),
                                interpolate=True, color="red", alpha=0.1)

                # Value labels
                offset_exp = df["Expenses"].max() * 0.03 if df["Expenses"].max() > 0 else 10
                offset_inc = df["Income"].max() * 0.03 if df["Income"].max() > 0 else 10
                offset_net = max(abs(df["Net"].max()), abs(df["Net"].min())) * 0.03

                for x, y in zip(df.index, df["Expenses"]):
                    ax.text(x, y + offset_exp, format_currency(y),
                            ha="center", va="bottom", fontsize=8, color="red")
                for x, y in zip(df.index, df["Income"]):
                    ax.text(x, y + offset_inc, format_currency(y),
                            ha="center", va="bottom", fontsize=8, color="green")
                for x, y in zip(df.index, df["Net"]):
                    va = "bottom" if y >= 0 else "top"
                    ax.text(x, y + (offset_net if y >= 0 else -offset_net),
                            format_currency(y), ha="center", va=va,
                            fontsize=8, color="green" if y >= 0 else "red",
                            fontweight="bold")

            else:
                # 📊 Stacked Bar Chart
                width = 20  # bar width in days
                ax.bar(df.index, df["Income"], width=width, color="green", label="Income")
                ax.bar(df.index, -df["Expenses"], width=width, color="red", label="Expenses")

                # Net as overlay line
                ax.plot(df.index, df["Net"], marker="o", markersize=6,
                        linewidth=2, linestyle="--", color="blue", label="Net Savings")

                # Labels for Income
                for x, y in zip(df.index, df["Income"]):
                    ax.text(x, y, format_currency(y),
                            ha="center", va="bottom", fontsize=8, color="green")

                # Labels for Expenses (plotted as negative)
                for x, y in zip(df.index, df["Expenses"]):
                    ax.text(x, -y, format_currency(y),
                            ha="center", va="top", fontsize=8, color="red")

                # Labels for Net Savings
                offset_net = max(abs(df["Net"].max()), abs(df["Net"].min())) * 0.03
                for x, y in zip(df.index, df["Net"]):
                    va = "bottom" if y >= 0 else "top"
                    ax.text(x, y + (offset_net if y >= 0 else -offset_net),
                            format_currency(y),
                            ha="center", va=va, fontsize=9,
                            color="blue", fontweight="bold")

            # Formatting
            ax.set_title(f"Cash Flow: {start_date:%b %Y} → {end_date:%b %Y}")
            ax.set_xlabel("Month")
            ax.set_ylabel("Amount (USD)")
            ax.legend()
            ax.grid(True, linestyle="--", alpha=0.7)

            # Format x-axis
            ax.set_xticks(df.index)
            ax.set_xticklabels([d.strftime("%b %Y") for d in df.index], rotation=45, ha="right")

            # Dynamic y padding
            ymin, ymax = ax.get_ylim()
            ax.set_ylim(ymin - abs(ymax) * 0.1, ymax + abs(ymax) * 0.1)

            fig.tight_layout()

            # Embed chart into Tkinter
            canvas = FigureCanvasTkAgg(fig, master=chart_frame)
            canvas.draw()
            canvas.get_tk_widget().pack(pady=10, fill="both", expand=True)

            # Export chart button
            def export_chart():
                filepath = filedialog.asksaveasfilename(
                    defaultextension=".png",
                    filetypes=[("PNG Image", "*.png")],
                    title="Save Cash Flow Report As",
                )
                if filepath:
                    try:
                        fig.savefig(filepath, dpi=150, bbox_inches="tight", pad_inches=0.2)
                        messagebox.showinfo(
                            "Export Successful",
                            f"Chart saved to:\n{os.path.abspath(filepath)}",
                        )
                    except Exception as error:
                        messagebox.showerror("Export Failed", str(error))

            ttk.Button(
                chart_frame,
                text="Export Chart as PNG",
                bootstyle="info",
                command=export_chart,
            ).pack(pady=5)

        # --------------------------------------------------------------
        # Bind events & render on load
        # --------------------------------------------------------------
        start_entry.bind("<<DateEntrySelected>>", generate_report)
        end_entry.bind("<<DateEntrySelected>>", generate_report)
        self.chart_type_combo.bind("<<ComboboxSelected>>", generate_report)

        # Initial render
        generate_report()

        # Back button
        ttk.Button(
            self.parent, text="Back",
            bootstyle="danger", command=self.back_callback
        ).pack(pady=5)
