# PROGRAM: Monthly Expenses Report
# PURPOSE: Display monthly expenses over time as a bar chart with the
#          ability to drill into details and export results.
# INPUT:
#   - parent (Frame): Parent Tkinter frame for rendering.
#   - username (str): Logged-in user requesting the report.
#   - back_callback (function): Callback to return to previous page.
# PROCESS:
#   - Retrieve all expenses within the chosen date range.
#   - Default to the last month with data (or current month if none).
#   - Group expenses by month and calculate totals.
#   - Render bar chart with clickable bars to show detail tables.
#   - Provide CSV and PNG export options.
# OUTPUT:
#   - Interactive monthly expenses chart with detail popups and export.
# HONOR CODE: On my honor, as an Aggie, I have neither given nor
#             received unauthorized aid on this academic work.

import os
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.ticker import StrMethodFormatter
import ttkbootstrap as ttk
from ttkbootstrap.widgets import DateEntry
from tkinter import filedialog, messagebox
from operations import reports
from analytics.helpers import build_table_popup, make_action_buttons


class MonthlyReport:
    """Page to display monthly expenses in bar chart format."""

    def __init__(self, parent, username, back_callback):
        """Initialize MonthlyReport."""
        self.parent = parent
        self.username = username
        self.back_callback = back_callback
        self._fig = None  # store latest figure for export

    def show(self):
        """Render the Monthly Expenses report page."""
        for widget in self.parent.winfo_children():
            widget.destroy()

        # Main frame
        frame = ttk.Frame(self.parent)
        frame.pack(fill="both", expand=True, padx=20, pady=20)

        # --------------------------------------------------------------
        # Determine default date range
        # --------------------------------------------------------------
        all_expenses = reports.get_user_expenses_range(
            self.username, "1900-01-01", "2999-12-31"
        )
        if not all_expenses.empty:
            last_date = all_expenses["date"].max().date()
            first_day = last_date.replace(day=1)
            next_month = (last_date.replace(day=28) +
                          pd.Timedelta(days=4)).replace(day=1)
            last_day = next_month - pd.Timedelta(days=1)
        else:
            today = pd.Timestamp.today().date()
            first_day = today.replace(day=1)
            next_month = (today.replace(day=28) +
                          pd.Timedelta(days=4)).replace(day=1)
            last_day = next_month - pd.Timedelta(days=1)

        # --------------------------------------------------------------
        # Date pickers
        # --------------------------------------------------------------
        ttk.Label(frame, text="Start Date:").grid(row=0, column=0, padx=5, pady=5)
        start_date = DateEntry(frame, bootstyle="primary", dateformat="%Y-%m-%d")
        start_date.set_date(first_day)
        start_date.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(frame, text="End Date:").grid(row=0, column=2, padx=5, pady=5)
        end_date = DateEntry(frame, bootstyle="primary", dateformat="%Y-%m-%d")
        end_date.set_date(last_day)
        end_date.grid(row=0, column=3, padx=5, pady=5)

        # --------------------------------------------------------------
        # Total spent label
        # --------------------------------------------------------------
        total_label = ttk.Label(
            frame,
            text="Total Spent: $0.00",
            font=("Helvetica", 12, "bold"),
            cursor="hand2",
        )
        total_label.grid(row=1, column=0, columnspan=4, pady=10)

        # --------------------------------------------------------------
        # Chart container
        # --------------------------------------------------------------
        chart_frame = ttk.Frame(frame)
        chart_frame.grid(row=2, column=0, columnspan=5, pady=20, sticky="nsew")
        frame.grid_rowconfigure(2, weight=1)
        frame.grid_columnconfigure(0, weight=1)

        # --------------------------------------------------------------
        # Chart refresh function
        # --------------------------------------------------------------
        def refresh_report(event=None):
            for widget in chart_frame.winfo_children():
                widget.destroy()

            df = reports.get_user_expenses_range(
                self.username,
                start_date.entry.get(),
                end_date.entry.get(),
            )

            total_spent = df["amount"].sum() if not df.empty else 0
            total_label.config(text=f"Total Spent: ${total_spent:,.2f}")
            total_label.df = df

            if df.empty:
                return

            monthly = df.groupby(df["date"].dt.to_period("M"))["amount"].sum()

            fig, ax = plt.subplots(figsize=(6, 4))
            bars = ax.bar(monthly.index.astype(str), monthly.values, picker=True)

            ax.set_title("Monthly Expenses")
            ax.set_ylabel("Amount ($)")
            ax.yaxis.set_major_formatter(StrMethodFormatter("${x:,.2f}"))
            fig.tight_layout()

            self._fig = fig

            canvas = FigureCanvasTkAgg(fig, master=chart_frame)
            canvas.draw()
            canvas.get_tk_widget().pack(fill="both", expand=True)

            # Drill-down on bar click
            def on_pick(event_pick):
                if (getattr(event_pick, "mouseevent", None) is None or
                        event_pick.mouseevent.button != 1):
                    return
                if isinstance(event_pick.artist, plt.Rectangle):
                    try:
                        idx = bars.index(event_pick.artist)
                        month_period = monthly.index[idx]
                        month_df = df[df["date"].dt.to_period("M") == month_period]
                        build_table_popup(
                            self.parent,
                            f"Expenses for {month_period}",
                            month_df,
                            export_name=f"{month_period}_expenses",
                        )
                    except ValueError:
                        pass

            fig.canvas.mpl_connect("pick_event", on_pick)

        # --------------------------------------------------------------
        # Export function
        # --------------------------------------------------------------
        def export_chart():
            if not self._fig:
                return
            filepath = filedialog.asksaveasfilename(
                defaultextension=".png",
                filetypes=[("PNG Image", "*.png")],
                title="Save Monthly Report As",
            )
            if filepath:
                self._fig.savefig(filepath, dpi=150, bbox_inches="tight", pad_inches=0.2)
                messagebox.showinfo(
                    "Export Successful",
                    f"Chart saved to:\n{os.path.abspath(filepath)}",
                )

        # --------------------------------------------------------------
        # Buttons (added once, not duplicated on refresh)
        # --------------------------------------------------------------
        make_action_buttons(
            self.parent,
            [
                ("Export Chart as PNG", export_chart, "info"),
                ("Back", self.back_callback, "danger"),
            ],
            width=25,
            use_grid=False,
        )

        # --------------------------------------------------------------
        # Bindings and initial render
        # --------------------------------------------------------------
        start_date.bind("<<DateEntrySelected>>", refresh_report)
        end_date.bind("<<DateEntrySelected>>", refresh_report)
        total_label.bind(
            "<Button-1>",
            lambda e: build_table_popup(
                self.parent,
                "All Expenses",
                getattr(total_label, "df", pd.DataFrame()),
            ),
        )

        refresh_report()
