# PROGRAM: Top Categories Report
# PURPOSE: Display top expense categories ranked by spending.
# INPUT:
#   - username (str): Logged-in user.
#   - parent (Frame): Parent Tkinter frame.
#   - back_callback (function): Callback for navigation.
# PROCESS:
#   - Retrieve expenses by date range.
#   - Aggregate totals by category.
#   - Show horizontal bar chart of top N categories.
#   - Allow export of chart.
# OUTPUT: Tkinter-embedded bar chart.
# HONOR CODE: On my honor, as an Aggie, I have neither given nor
#             received unauthorized aid on this academic work.

import os
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
from tkinter import filedialog, messagebox
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import ttkbootstrap as ttk
from ttkbootstrap.widgets import DateEntry
from operations.finance_operations import FinanceOperations
from analytics.helpers import make_action_buttons


class TopCategoriesReport:
    """Page to display top expense categories."""

    def __init__(self, parent, username, back_callback):
        self.parent = parent
        self.username = username
        self.back_callback = back_callback
        self.finance_ops = FinanceOperations()
        self._fig = None

    def show(self):
        """Render the Top Categories report page."""
        for widget in self.parent.winfo_children():
            widget.destroy()

        # Configure grid
        self.parent.grid_rowconfigure(2, weight=1)
        self.parent.grid_columnconfigure(0, weight=1)

        ttk.Label(self.parent, text="Top Spending Categories", font=("Helvetica", 14, "bold")).grid(row=0, column=0, pady=10)

        # Controls
        control_frame = ttk.Frame(self.parent, padding=10)
        control_frame.grid(row=1, column=0, sticky="ew")

        ttk.Label(control_frame, text="Start Date:").grid(row=0, column=0, sticky="w")
        start_entry = DateEntry(control_frame, bootstyle="info", dateformat="%Y-%m-%d")
        start_entry.set_date(datetime.today().replace(day=1))
        start_entry.grid(row=0, column=1, padx=5)

        ttk.Label(control_frame, text="End Date:").grid(row=0, column=2, sticky="w")
        end_entry = DateEntry(control_frame, bootstyle="info", dateformat="%Y-%m-%d")
        end_entry.set_date(datetime.today())
        end_entry.grid(row=0, column=3, padx=5)

        ttk.Label(control_frame, text="Show Top:").grid(row=0, column=4, padx=(15, 0), sticky="w")
        topn_combo = ttk.Combobox(control_frame, values=[5, 10, 20], width=5, state="readonly")
        topn_combo.set(10)
        topn_combo.grid(row=0, column=5, padx=5)

        # Chart frame
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
            topn = int(topn_combo.get())

            expenses = self.finance_ops.get_user_expenses(self.username)
            if not expenses:
                ttk.Label(chart_frame, text="No expenses available").grid()
                return

            df = pd.DataFrame(expenses, columns=["id", "date", "category", "amount", "description"])
            df["date"] = pd.to_datetime(df["date"], errors="coerce")
            df = df[(df["date"] >= pd.to_datetime(start_date)) & (df["date"] <= pd.to_datetime(end_date))]

            if df.empty:
                ttk.Label(chart_frame, text="No expenses in this range").grid()
                return

            df = df.groupby("category")["amount"].sum().reset_index().sort_values("amount", ascending=False).head(topn)
            n = len(df)

            fig, ax = plt.subplots(figsize=(8, max(4, 0.5 * n)))
            colors = plt.cm.tab10(range(n))
            bars = ax.barh(df["category"], df["amount"], color=colors)

            for bar, amount in zip(bars, df["amount"]):
                ax.text(bar.get_width() + (0.01 * df["amount"].max()), bar.get_y() + bar.get_height() / 2,
                        f"${amount:,.2f}", va="center", ha="left", fontsize=9)

            ax.set_title(f"Top {topn} Categories: {start_date:%Y-%m-%d} → {end_date:%Y-%m-%d}")
            ax.set_xlabel("Amount (USD)")
            ax.invert_yaxis()
            fig.tight_layout()
            self._fig = fig

            canvas = FigureCanvasTkAgg(fig, master=chart_frame)
            canvas.draw()
            canvas.get_tk_widget().grid(row=0, column=0, sticky="nsew")

        # Export
        def export_chart():
            if not self._fig:
                return
            filepath = filedialog.asksaveasfilename(defaultextension=".png", filetypes=[("PNG Image", "*.png")], title="Save Top Categories Report As")
            if filepath:
                self._fig.savefig(filepath, dpi=150, bbox_inches="tight", pad_inches=0.2)
                messagebox.showinfo("Export Successful", f"Chart saved to:\n{os.path.abspath(filepath)}")

        # Buttons once
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
        topn_combo.bind("<<ComboboxSelected>>", generate_report)

        generate_report()
