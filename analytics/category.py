# PROGRAM: Category Report
# PURPOSE: Visualize expenses grouped by category for a user within a date range.
# INPUT:
#   - username (str): Logged-in user whose expense data will be analyzed.
#   - parent (Frame): Parent tkinter frame where the chart UI will be rendered.
#   - back_callback (function): Callback function to return to the previous page.
# PROCESS:
#   - Retrieve user expenses from SQLite via `reports.get_user_expenses_range`.
#   - Default to last month with available data (or current month if none).
#   - Filter data by start/end dates using pandas.
#   - Group expenses by category and display as a pie chart.
#   - Add interactive slice click → popup table of detailed transactions.
#   - Provide export option for chart as PNG.
# OUTPUT:
#   - Tkinter-embedded pie chart with percentage and dollar values per category.
#   - Interactive table popup on category click.
# HONOR CODE: On my honor, as an Aggie, I have neither given nor
#             received unauthorized aid on this academic work.

import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import ttkbootstrap as ttk
import pandas as pd
from ttkbootstrap.widgets import DateEntry
from operations import reports
from .helpers import build_table_popup
from tkinter import filedialog, messagebox
import os


class CategoryReport:
    """Page to display expenses grouped by category (pie chart)."""

    def __init__(self, parent, username, back_callback):
        """
        Initialize the Category Report page.

        Args:
            parent: Tkinter parent frame.
            username (str): Logged-in user whose expenses are shown.
            back_callback (function): Callback to navigate back.
        """
        self.parent = parent
        self.username = username
        self.back_callback = back_callback

    def show(self):
        """Render the Category Report page."""
        # --------------------------------------------------------------
        # Clear parent frame
        # --------------------------------------------------------------
        for w in self.parent.winfo_children():
            w.destroy()

        frame = ttk.Frame(self.parent)
        frame.pack(fill="both", expand=True, padx=20, pady=20)

        # --------------------------------------------------------------
        # Default to last month with data (fallback = current month)
        # --------------------------------------------------------------
        all_expenses = reports.get_user_expenses_range(
            self.username, "1900-01-01", "2999-12-31"
        )

        if not all_expenses.empty:
            last_date = all_expenses["date"].max().date()
            first_day = last_date.replace(day=1)
            next_month = (last_date.replace(day=28) + pd.Timedelta(days=4)).replace(day=1)
            last_day = next_month - pd.Timedelta(days=1)
        else:
            today = pd.Timestamp.today().date()
            first_day = today.replace(day=1)
            next_month = (today.replace(day=28) + pd.Timedelta(days=4)).replace(day=1)
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
        # Total Spent Label
        # --------------------------------------------------------------
        total_label = ttk.Label(
            frame,
            text="Total Spent: $0.00",
            font=("Helvetica", 12, "bold"),
            cursor="hand2"
        )
        total_label.grid(row=1, column=0, columnspan=4, pady=10)

        # Chart container
        chart_frame = ttk.Frame(frame)
        chart_frame.grid(row=2, column=0, columnspan=5, pady=20)

        # --------------------------------------------------------------
        # Refresh function
        # --------------------------------------------------------------
        def refresh_report(event=None):
            """Update chart and total spent label based on date range."""
            start = start_date.entry.get()
            end = end_date.entry.get()
            df = reports.get_user_expenses_range(self.username, start, end)

            total_spent = df["amount"].sum() if not df.empty else 0
            total_label.config(text=f"Total Spent: ${total_spent:,.2f}")
            total_label.df = df

            for w in chart_frame.winfo_children():
                w.destroy()

            if not df.empty:
                grouped = df.groupby("category")["amount"].sum().reset_index()

                fig, ax = plt.subplots(figsize=(6, 4))

                def autopct_format(pct, allvals):
                    """Format pie chart labels with percentage and $ amount."""
                    absolute = int(round(pct / 100.0 * sum(allvals)))
                    return f"{pct:.1f}%\n(${absolute:,.0f})"

                wedges, _, _ = ax.pie(
                    grouped["amount"],
                    labels=grouped["category"],
                    autopct=lambda pct: autopct_format(pct, grouped["amount"]),
                    startangle=90
                )
                ax.set_title("Expenses by Category")

                # --- Slice click → popup table
                def on_pick(event):
                    for i, wedge in enumerate(wedges):
                        if event.artist == wedge:
                            category = grouped.iloc[i]["category"]
                            cat_df = df[df["category"] == category]
                            build_table_popup(
                                self.parent,
                                f"Expenses for {category}",
                                cat_df,
                                export_name=f"{category}_expenses"
                            )
                            break

                for wedge in wedges:
                    wedge.set_picker(True)

                fig.canvas.mpl_connect("pick_event", on_pick)

                # Embed chart
                canvas = FigureCanvasTkAgg(fig, master=chart_frame)
                canvas.draw()
                canvas.get_tk_widget().pack(fill="both", expand=True)

                # --- Export Chart Button
                def export_chart():
                    filepath = filedialog.asksaveasfilename(
                        defaultextension=".png",
                        filetypes=[("PNG Image", "*.png")],
                        title="Save Category Report As"
                    )
                    if filepath:
                        try:
                            fig.savefig(filepath, dpi=150)
                            messagebox.showinfo(
                                "Export Successful",
                                f"Chart saved to:\n{os.path.abspath(filepath)}"
                            )
                        except Exception as e:
                            messagebox.showerror("Export Failed", str(e))

                ttk.Button(
                    chart_frame, text="Export Chart as PNG",
                    bootstyle="info", command=export_chart
                ).pack(pady=10)

                ttk.Button(
                    chart_frame, text="Back",
                    bootstyle="secondary", width=20,
                    command=self.back_callback
                ).pack(pady=10)

        # --------------------------------------------------------------
        # Event bindings
        # --------------------------------------------------------------
        start_date.bind("<<DateEntrySelected>>", refresh_report)
        end_date.bind("<<DateEntrySelected>>", refresh_report)
        total_label.bind(
            "<Button-1>",
            lambda e: build_table_popup(
                self.parent,
                "All Expenses",
                getattr(total_label, "df", pd.DataFrame())
            )
        )

        # Initial load
        refresh_report()
