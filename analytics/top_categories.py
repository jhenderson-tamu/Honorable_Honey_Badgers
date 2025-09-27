# PROGRAM: Top Categories Report
# PURPOSE: Display top expense categories ranked by spending with date
#          filtering, automatic updates, and configurable top N categories.
# INPUT:
#   - parent (Frame): Parent tkinter frame for rendering content.
#   - username (str): Logged-in user requesting report.
#   - back_callback (function): Callback to return to previous page.
# PROCESS:
#   - Retrieve all expenses for the user.
#   - Filter results by selected date range.
#   - Group by category, rank by total spending, select top N.
#   - Render horizontal bar chart with USD labels.
#   - Provide export option for chart as PNG.
# OUTPUT:
#   - Interactive horizontal bar chart embedded in tkinter frame.
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
from operations.finance_operations import FinanceOperations


class TopCategoriesReport:
    """Page to display top expense categories with date filtering."""

    def __init__(self, parent, username, back_callback):
        """
        Initialize TopCategoriesReport.

        Args:
            parent (Frame): Parent tkinter frame.
            username (str): Logged-in username.
            back_callback (function): Function to return to previous page.
        """
        self.parent = parent
        self.username = username
        self.back_callback = back_callback
        self.finance_ops = FinanceOperations()

    # ------------------------------------------------------------------
    # Public
    # ------------------------------------------------------------------
    def show(self):
        """Render the Top Categories report page."""
        # Clear parent frame
        for w in self.parent.winfo_children():
            w.destroy()

        ttk.Label(
            self.parent,
            text="Top Spending Categories",
            font=("Helvetica", 14, "bold"),
        ).pack(pady=10)

        # --------------------------------------------------------------
        # Date pickers + Top N selector
        # --------------------------------------------------------------
        control_frame = ttk.Frame(self.parent, padding=10)
        control_frame.pack(fill="x")

        ttk.Label(control_frame, text="Start Date:").grid(
            row=0, column=0, sticky="w"
        )
        start_entry = DateEntry(
            control_frame, bootstyle="info", dateformat="%Y-%m-%d"
        )
        start_entry.set_date(datetime.today().replace(day=1))
        start_entry.grid(row=0, column=1, padx=5)

        ttk.Label(control_frame, text="End Date:").grid(
            row=0, column=2, sticky="w"
        )
        end_entry = DateEntry(
            control_frame, bootstyle="info", dateformat="%Y-%m-%d"
        )
        end_entry.set_date(datetime.today())
        end_entry.grid(row=0, column=3, padx=5)

        # Top N selector
        ttk.Label(control_frame, text="Show Top:").grid(
            row=0, column=4, sticky="w", padx=(15, 0)
        )
        topn_combo = ttk.Combobox(
            control_frame,
            values=[5, 10, 20],
            width=5,
            state="readonly",
        )
        topn_combo.set(10)  # default
        topn_combo.grid(row=0, column=5, padx=5)

        # Chart container
        chart_frame = ttk.Frame(self.parent, padding=10)
        chart_frame.pack(fill="both", expand=True)

        # --------------------------------------------------------------
        # Chart Generator
        # --------------------------------------------------------------
        def generate_report(*args):
            """Build chart for current date range selection."""
            for w in chart_frame.winfo_children():
                w.destroy()

            start_date = start_entry.get_date()
            end_date = end_entry.get_date()
            topn = int(topn_combo.get())

            # Fetch all expenses
            expenses = self.finance_ops.get_user_expenses(self.username)
            if not expenses:
                ttk.Label(chart_frame, text="No expenses available").pack(
                    pady=10
                )
                return

            # Convert to DataFrame
            df = pd.DataFrame(
                expenses,
                columns=[
                    "id",
                    "date",
                    "category",
                    "amount",
                    "description",
                ],
            )
            df["date"] = pd.to_datetime(df["date"], errors="coerce")

            # Filter by date range
            mask = (
                (df["date"] >= pd.to_datetime(start_date))
                & (df["date"] <= pd.to_datetime(end_date))
            )
            df = df.loc[mask]

            if df.empty:
                ttk.Label(
                    chart_frame, text="No expenses in this date range"
                ).pack(pady=10)
                return

            # Group, sort, top N
            df = df.groupby("category")["amount"].sum().reset_index()
            df = df.sort_values("amount", ascending=False).head(topn)

            # Dynamic chart sizing
            n = len(df)
            fig, ax = plt.subplots(figsize=(8, max(4, 0.5 * n)))

            colors = plt.cm.tab10(range(n))
            bars = ax.barh(df["category"], df["amount"], color=colors)

            ax.set_xlabel("Amount (USD)")
            ax.set_ylabel("Category")
            ax.set_title(
                f"Top {topn} Categories: {start_date:%Y-%m-%d} → {end_date:%Y-%m-%d}"
            )
            ax.invert_yaxis()

            # Labels with smart placement
            max_amount = max(df["amount"])
            for bar, amount in zip(bars, df["amount"]):
                if bar.get_width() > max_amount * 0.2:  # >= 20% of max → inside
                    ax.text(
                        bar.get_width() - (0.01 * max_amount),
                        bar.get_y() + bar.get_height() / 2,
                        f"${amount:,.2f}",
                        va="center",
                        ha="right",
                        fontsize=9,
                        color="white",
                        fontweight="bold"
                    )
                else:  # smaller bars → outside
                    ax.text(
                        bar.get_width() + (0.01 * max_amount),
                        bar.get_y() + bar.get_height() / 2,
                        f"${amount:,.2f}",
                        va="center",
                        ha="left",
                        fontsize=9,
                        color="black"
                    )

            ax.tick_params(axis="y", labelsize=9)
            fig.tight_layout()

            # Embed into tkinter
            canvas = FigureCanvasTkAgg(fig, master=chart_frame)
            canvas.draw()
            canvas.get_tk_widget().pack(pady=10, fill="both", expand=True)

            # Export chart button
            def export_chart():
                filepath = filedialog.asksaveasfilename(
                    defaultextension=".png",
                    filetypes=[("PNG Image", "*.png")],
                    title="Save Top Categories Report As",
                )
                if filepath:
                    try:
                        fig.savefig(filepath, dpi=150, bbox_inches="tight", pad_inches=0.2)
                        messagebox.showinfo(
                            "Export Successful",
                            f"Chart saved to:\n{os.path.abspath(filepath)}"
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
        # Bindings & Load
        # --------------------------------------------------------------
        start_entry.bind("<<DateEntrySelected>>", generate_report)
        end_entry.bind("<<DateEntrySelected>>", generate_report)
        topn_combo.bind("<<ComboboxSelected>>", generate_report)

        # Initial load
        generate_report()

        # --------------------------------------------------------------
        # Back button
        # --------------------------------------------------------------
        ttk.Button(
            self.parent,
            text="Back",
            bootstyle="secondary",
            command=self.back_callback,
        ).pack(pady=5)
