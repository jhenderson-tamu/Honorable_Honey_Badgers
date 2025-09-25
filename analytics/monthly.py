# PROGRAM: Monthly Expenses Report
# PURPOSE: Display monthly expenses over time as a bar chart with the
#          ability to drill into details and export results.
# INPUT:
#   - parent (Frame): Parent tkinter frame for rendering.
#   - username (str): Logged-in user requesting the report.
#   - back_callback (function): Callback to return to previous page.
# PROCESS:
#   - Retrieve all expenses within the chosen date range.
#   - Default to the last month with data (or current month if none).
#   - Group expenses by month and calculate totals.
#   - Render bar chart with clickable bars to show detail tables.
#   - Provide CSV and PNG export options.
# OUTPUT:
#   - Interactive monthly expenses chart with detail popups and export
#     functionality.
# HONOR CODE: On my honor, as an Aggie, I have neither given nor
#             received unauthorized aid on this academic work.

import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.ticker import StrMethodFormatter
import ttkbootstrap as ttk
import pandas as pd
from ttkbootstrap.widgets import DateEntry
from operations import reports
from .helpers import build_table_popup
from tkinter import filedialog, messagebox
import os


class MonthlyReport:
    """Page to display monthly expenses in bar chart format."""

    def __init__(self, parent, username, back_callback):
        """
        Initialize MonthlyReport.

        Args:
            parent (Frame): Parent tkinter frame.
            username (str): Logged-in username.
            back_callback (function): Function to return to previous page.
        """
        self.parent = parent
        self.username = username
        self.back_callback = back_callback

    # ------------------------------------------------------------------
    # Public
    # ------------------------------------------------------------------
    def show(self):
        """Render the monthly expenses report page."""
        # Clear frame
        for w in self.parent.winfo_children():
            w.destroy()

        frame = ttk.Frame(self.parent)
        frame.pack(fill="both", expand=True, padx=20, pady=20)

        # --------------------------------------------------------------
        # Default date range = last month with data (or current month)
        # --------------------------------------------------------------
        all_expenses = reports.get_user_expenses_range(
            self.username, "1900-01-01", "2999-12-31"
        )

        if not all_expenses.empty:
            last_date = all_expenses["date"].max().date()
            first_day = last_date.replace(day=1)
            next_month = (
                last_date.replace(day=28) + pd.Timedelta(days=4)
            ).replace(day=1)
            last_day = next_month - pd.Timedelta(days=1)
        else:
            today = pd.Timestamp.today().date()
            first_day = today.replace(day=1)
            next_month = (
                today.replace(day=28) + pd.Timedelta(days=4)
            ).replace(day=1)
            last_day = next_month - pd.Timedelta(days=1)

        min_date, max_date = first_day, last_day

        # --------------------------------------------------------------
        # Date pickers
        # --------------------------------------------------------------
        ttk.Label(frame, text="Start Date:").grid(row=0, column=0, padx=5, pady=5)
        start_date = DateEntry(frame, bootstyle="primary", dateformat="%Y-%m-%d")
        start_date.set_date(min_date)
        start_date.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(frame, text="End Date:").grid(row=0, column=2, padx=5, pady=5)
        end_date = DateEntry(frame, bootstyle="primary", dateformat="%Y-%m-%d")
        end_date.set_date(max_date)
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

        # Chart container
        chart_frame = ttk.Frame(frame)
        chart_frame.grid(row=2, column=0, columnspan=5, pady=20)

        # --------------------------------------------------------------
        # Handlers
        # --------------------------------------------------------------
        def show_month_details(month_period, month_df):
            """Open popup with details for a specific month."""
            build_table_popup(
                self.parent,
                f"Expenses for {month_period}",
                month_df,
                export_name=f"{month_period}_expenses",
            )

        def show_all_details(event=None):
            """Open popup with all expenses in the current report."""
            df = getattr(total_label, "df", pd.DataFrame())
            build_table_popup(
                self.parent, "All Expenses", df, export_name="expenses"
            )

        def refresh_report(event=None):
            """Reload chart and labels when date range changes."""
            start = start_date.entry.get()
            end = end_date.entry.get()
            df = reports.get_user_expenses_range(self.username, start, end)

            # Update total spent
            total_spent = df["amount"].sum() if not df.empty else 0
            total_label.config(text=f"Total Spent: ${total_spent:,.2f}")
            total_label.df = df

            # Clear previous chart
            for w in chart_frame.winfo_children():
                w.destroy()

            if not df.empty:
                # Group by month
                monthly = df.groupby(df["date"].dt.to_period("M"))[
                    "amount"
                ].sum()

                fig, ax = plt.subplots(figsize=(6, 4))
                bar_container = ax.bar(
                    monthly.index.astype(str),
                    monthly.values,
                    picker=True,
                )
                ax.set_title("Monthly Expenses")
                ax.set_ylabel("Amount ($)")
                fig.tight_layout()

                # Format y-axis as USD
                ax.yaxis.set_major_formatter(StrMethodFormatter("${x:,.2f}"))

                # Embed chart in tkinter
                canvas = FigureCanvasTkAgg(fig, master=chart_frame)
                canvas.draw()
                canvas.get_tk_widget().pack(fill="both", expand=True)

                # Click bar to see details
                def on_pick(event):
                    if (
                        isinstance(event.artist, plt.Rectangle)
                        and event.artist in bar_container
                    ):
                        bar_index = bar_container.index(event.artist)
                        month_period = monthly.index[bar_index]
                        month_df = df[
                            df["date"].dt.to_period("M") == month_period
                        ]
                        show_month_details(month_period, month_df)

                fig.canvas.mpl_connect("pick_event", on_pick)

                # Export chart button
                def export_chart():
                    filepath = filedialog.asksaveasfilename(
                        defaultextension=".png",
                        filetypes=[("PNG Image", "*.png")],
                        title="Save Monthly Report As",
                    )
                    if filepath:
                        try:
                            fig.savefig(filepath, dpi=150)
                            messagebox.showinfo(
                                "Export Successful",
                                f"Chart saved to:\n{os.path.abspath(filepath)}",
                            )
                        except Exception as e:
                            messagebox.showerror("Export Failed", str(e))

                ttk.Button(
                    chart_frame,
                    text="Export Chart as PNG",
                    bootstyle="info",
                    command=export_chart,
                ).pack(pady=10)

                ttk.Button(
                    frame,
                    text="Back",
                    bootstyle="secondary",
                    width=20,
                    command=self.back_callback,
                ).grid(row=3, column=0, columnspan=5, pady=10)

        # --------------------------------------------------------------
        # Bindings and initial load
        # --------------------------------------------------------------
        start_date.bind("<<DateEntrySelected>>", refresh_report)
        end_date.bind("<<DateEntrySelected>>", refresh_report)
        total_label.bind("<Button-1>", show_all_details)

        refresh_report()
