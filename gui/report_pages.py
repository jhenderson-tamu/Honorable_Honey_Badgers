# PROGRAM: Expense Management Pages
# PURPOSE: Provide pages for adding, importing, viewing, and removing
# user expenses, including category management.
# INPUT: Username of the logged-in user and the parent frame for display.
# PROCESS: Creates GUI pages to manage expenses, interact with
# FinanceOperations to store/retrieve data, and updates the interface
# dynamically.
# OUTPUT: User-entered expenses saved to database, displayed expense
# tables, or success/error messages in the GUI.
# HONOR CODE: On my honor, as an Aggie, I have neither given nor
# received unauthorized aid on this academic work.

import tkinter as tk
import ttkbootstrap as ttk
from ttkbootstrap.constants import NORMAL, DISABLED
from ttkbootstrap.dialogs import Messagebox
from tkinter import filedialog, StringVar
import os
from operations.finance_operations import FinanceOperations
from operations import reports
from pathlib import Path
from datetime import datetime
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from io import BytesIO
from PIL import Image, ImageTk
import pandas as pd

class ReportPages:
    """Class to handle expense-related GUI pages."""

    def __init__(self, username: str, parent_frame):
        """
        Initialize ReportsPages.

        Args:
            username (str): Username of the logged-in user.
            parent_frame: The frame where expense pages will be displayed.
        """
        self.username = username
        self.parent_frame = parent_frame
        self.finance_ops = FinanceOperations()

    # ------------------------------------------------------------------
    # Main Reports Menu
    # ------------------------------------------------------------------
    def create_report_page(self):
        """Create the main expenses menu with available options."""
        self._clear_parent_frame()

        ttk.Label(
            self.parent_frame,
            text=f"Report Options for {self.username}",
            font=("Helvetica", 14, "bold")
        ).pack(pady=15)

        frame = ttk.Frame(self.parent_frame, padding=20)
        frame.pack(fill="both", expand=True)

        # Menu Buttons

        ttk.Button(
            frame, text="Generate Reports", bootstyle="success", width=20,
            command=self.generate_reports_page
        ).pack(pady=10)

        ttk.Button(
            frame, text="Close Reports Page", bootstyle="danger", width=20,
            command=self.close_report_page
        ).pack(pady=20)

    def close_report_page(self):
        """Close the expense page by clearing all widgets."""
        self._clear_parent_frame()

    # ------------------------------------------------------------------
    # Generate Reports
    # ------------------------------------------------------------------

    def generate_reports_page(self):
        """Select date range, run reports, and display multiple chart thumbnails that expand on click."""

        self._clear_parent_frame()

        ttk.Label(
            self.parent_frame,
            text=f"Generate Reports for {self.username}",
            font=("Helvetica", 14, "bold")
        ).pack(pady=15)

        # --- Date Range Selection ---
        date_frame = ttk.Frame(self.parent_frame, padding=10)
        date_frame.pack(pady=5, fill="x")

        ttk.Label(date_frame, text="Start Date:").grid(row=0, column=0, padx=5,
                                                       sticky="w")
        start_date_entry = ttk.DateEntry(
            date_frame, bootstyle="info", dateformat="%Y-%m-%d"
        )
        start_date_entry.set_date(datetime.today().replace(month=1, day=1))
        start_date_entry.grid(row=0, column=1, padx=5)

        ttk.Label(date_frame, text="End Date:").grid(row=0, column=2, padx=5,
                                                     sticky="w")
        end_date_entry = ttk.DateEntry(
            date_frame, bootstyle="info", dateformat="%Y-%m-%d"
        )
        end_date_entry.set_date(datetime.today())
        end_date_entry.grid(row=0, column=3, padx=5)

        # Scrollable frame for thumbnails
        canvas = tk.Canvas(self.parent_frame)
        scrollbar = ttk.Scrollbar(self.parent_frame, orient="horizontal",
                                  command=canvas.xview)
        scroll_frame = ttk.Frame(canvas)

        scroll_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scroll_frame, anchor="nw")
        canvas.configure(xscrollcommand=scrollbar.set)

        canvas.pack(fill="both", expand=True, pady=10)
        scrollbar.pack(fill="x")

        # Store thumbnail references
        self.thumbnails = []

        def create_chart_thumbnail(categories, totals, width=200, height=150):
            """Create a thumbnail chart image."""
            fig, ax = plt.subplots(figsize=(width / 100, height / 100), dpi=100)
            ax.bar(categories, totals, color="skyblue")
            ax.set_xticks(range(len(categories)))
            ax.set_xticklabels(categories, rotation=45, fontsize=8)
            ax.set_yticklabels(ax.get_yticks(), fontsize=8)
            ax.set_title("Expenses", fontsize=10)
            fig.tight_layout()

            buf = BytesIO()
            fig.savefig(buf, format="png")
            plt.close(fig)
            buf.seek(0)
            image = Image.open(buf)
            return ImageTk.PhotoImage(image)

        def run_reports():
            """Generate reports, create thumbnails, and display them."""
            for widget in scroll_frame.winfo_children():
                widget.destroy()
            self.thumbnails.clear()

            db_path = Path("data/finance.db")
            start_date = start_date_entry.entry.get()
            end_date = end_date_entry.entry.get()

            # Generate reports (CSV/Excel)
            result = reports.generate_reports(db_path, self.username,
                                              start_date, end_date)
            ttk.Label(
                self.parent_frame,
                text=f"Reports saved in: {result['output_dir']}",
                foreground="green"
            ).pack(pady=5)

            try:
                # Read CSV or fallback to database
                report_csv = Path(
                    result["output_dir"]) / f"{self.username}_expenses.csv"
                if report_csv.exists():
                    df = pd.read_csv(report_csv)
                else:
                    import sqlite3
                    conn = sqlite3.connect(db_path)
                    df = pd.read_sql(
                        "SELECT category, amount FROM expenses "
                        "WHERE username=? AND date BETWEEN ? AND ?",
                        conn, params=(self.username, start_date, end_date)
                    )
                    conn.close()

                if df.empty:
                    raise ValueError(
                        "No expenses found for the selected period.")

                # Aggregate by category
                summary_df = df.groupby("category")[
                    "amount"].sum().reset_index()
                summary_list = summary_df.rename(
                    columns={"category": "Category",
                             "amount": "Total"}).to_dict(orient="records")

                # Create thumbnail
                categories = [row["Category"] for row in summary_list]
                totals = [float(row["Total"]) for row in summary_list]
                thumb_image = create_chart_thumbnail(categories, totals)
                self.thumbnails.append(
                    thumb_image)  # prevent garbage collection

                # Display thumbnail as button
                btn = ttk.Button(scroll_frame, image=thumb_image)
                btn.image = thumb_image
                btn.grid(row=0, column=0, padx=5, pady=5)

                # Click opens full-size chart
                def show_full_chart(categories=categories, totals=totals):
                    top = tk.Toplevel(self.parent_frame)
                    top.title("Full Chart")
                    fig, ax = plt.subplots(figsize=(6, 4))
                    ax.bar(categories, totals, color="skyblue")
                    ax.set_title("Expenses by Category")
                    ax.set_ylabel("Total ($)")
                    ax.set_xlabel("Category")
                    ax.tick_params(axis="x", rotation=45)

                    canvas_full = FigureCanvasTkAgg(fig, master=top)
                    canvas_full.draw()
                    canvas_full.get_tk_widget().pack(fill="both", expand=True)

                btn.config(command=show_full_chart)

            except Exception as e:
                ttk.Label(
                    self.parent_frame,
                    text=f"No report data available: {e}",
                    foreground="red"
                ).pack(pady=10)

        ttk.Button(
            self.parent_frame,
            text="Run Reports",
            bootstyle="success",
            command=run_reports
        ).pack(pady=10)

        ttk.Button(
            self.parent_frame,
            text="Back to Expenses",
            bootstyle="danger",
            command=self.create_report_page
        ).pack(pady=10)

    # ------------------------------------------------------------------
    # Helper Method
    # ------------------------------------------------------------------
    def _clear_parent_frame(self):
        """Clear all widgets from the parent frame."""
        for widget in self.parent_frame.winfo_children():
            widget.destroy()
