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
        Initialize ExpensePages.

        Args:
            username (str): Username of the logged-in user.
            parent_frame: The frame where expense pages will be displayed.
        """
        self.username = username
        self.parent_frame = parent_frame
        self.finance_ops = FinanceOperations()

    # ------------------------------------------------------------------
    # Main Expense Menu
    # ------------------------------------------------------------------
    def create_report_page(self):
        """Create the main expenses menu with available options."""
        self._clear_parent_frame()

        ttk.Label(
            self.parent_frame,
            text=f"Expense Options for {self.username}",
            font=("Helvetica", 14, "bold")
        ).pack(pady=15)

        frame = ttk.Frame(self.parent_frame, padding=20)
        frame.pack(fill="both", expand=True)

        # Menu Buttons
        ttk.Button(
            frame, text="Manual Entry", bootstyle="primary", width=20,
            command=self.expense_entry_page
        ).pack(pady=10)

        ttk.Button(
            frame, text="Import Expense", bootstyle="primary", width=20,
            command=self.import_expenses_csv
        ).pack(pady=10)

        ttk.Button(
            frame, text="View Expenses", bootstyle="primary", width=20,
            command=self.view_expenses_page
        ).pack(pady=10)

        ttk.Button(
            frame, text="Remove Expenses", bootstyle="primary", width=20,
            command=self.remove_expenses_page
        ).pack(pady=10)

        ttk.Button(
            frame, text="Generate Reports", bootstyle="success", width=20,
            command=self.generate_reports_page
        ).pack(pady=10)

        ttk.Button(
            frame, text="Close Expense Page", bootstyle="danger", width=20,
            command=self.close_expense_page
        ).pack(pady=20)

    def close_expense_page(self):
        """Close the expense page by clearing all widgets."""
        self._clear_parent_frame()

    # ------------------------------------------------------------------
    # Expense Entry Page
    # ------------------------------------------------------------------
    def expense_entry_page(self):
        """Create the manual expense entry page."""
        self._clear_parent_frame()

        ttk.Label(
            self.parent_frame,
            text=f"Manual Expense Entry for {self.username}",
            font=("Helvetica", 14, "bold")
        ).pack(pady=15)

        form_frame = ttk.Frame(self.parent_frame, padding=20)
        form_frame.pack(fill="both", expand=True)

        # --- Form Fields ---
        ttk.Label(form_frame, text="Description:").pack(anchor="w")
        desc_entry = ttk.Entry(form_frame)
        desc_entry.pack(fill="x", pady=5)

        ttk.Label(form_frame, text="Amount:").pack(anchor="w")
        amount_entry = ttk.Entry(form_frame)
        amount_entry.pack(fill="x", pady=5)

        ttk.Label(form_frame, text="Date (YYYY-MM-DD):").pack(anchor="w")
        date_entry = ttk.DateEntry(
            form_frame, bootstyle="info", dateformat="%Y-%m-%d"
        )
        date_entry.set_date(datetime.today())
        date_entry.pack(fill="x", pady=5)

        ttk.Label(form_frame, text="Select Category:").pack(anchor="w")
        category_var = tk.StringVar()
        category_menu = ttk.Combobox(
            form_frame, textvariable=category_var,
            values=self.finance_ops.load_expense_categories(),
            state="readonly"
        )
        category_menu.set("Select Category")
        category_menu.pack(fill="x", pady=5)

        ttk.Label(form_frame, text="Or Add New Category:").pack(anchor="w")
        new_category_entry = ttk.Entry(form_frame)
        new_category_entry.pack(fill="x", pady=5)

        notification_label = ttk.Label(
            form_frame, text="", foreground="green",
            font=("Helvetica", 12, "italic"), anchor="center", justify="center"
        )
        notification_label.pack(pady=(0, 10))

        # --- Helper Functions ---
        def show_notification(message, type="info"):
            """Show a notification message for a few seconds."""
            color = {"info": "green", "error": "red"}.get(type, "black")
            notification_label.config(text=message, foreground=color)
            notification_label.after(
                3000, lambda: notification_label.config(text="")
            )

        def add_category():
            """Add a new expense category to the database."""
            new_cat = new_category_entry.get().strip()
            if not new_cat:
                show_notification("Category name cannot be empty.", "error")
                return

            success, message = self.finance_ops.add_expense_category(new_cat)
            show_notification(message, "info" if success else "error")

            if success:
                new_category_entry.delete(0, "end")
                category_menu.config(
                    values=self.finance_ops.load_expense_categories()
                )
                category_var.set(new_cat)

        def save_expense():
            """Validate and save the expense to the database."""
            date_obj = date_entry.get_date()
            date = date_obj.strftime("%Y-%m-%d")
            desc = desc_entry.get().strip()
            amount = amount_entry.get().strip()
            category = category_var.get().strip()

            if not (date and desc and amount and category):
                show_notification("All fields are required!", "error")
                return

            if category == "Select Category":
                show_notification("Please select a category.", "error")
                return

            try:
                amount = float(amount)
            except ValueError:
                show_notification("Amount must be a number.", "error")
                return

            success, message = self.finance_ops.add_expense(
                date, desc, category, amount, self.username
            )
            show_notification(message, "info" if success else "error")

            if success:
                desc_entry.delete(0, "end")
                amount_entry.delete(0, "end")
                category_var.set("Select Category")
                date_entry.set_date(datetime.today())

        # --- Buttons ---
        ttk.Button(
            form_frame, text="Add Category", bootstyle="info",
            command=add_category
        ).pack(pady=5)
        ttk.Button(
            form_frame, text="Save Expense", bootstyle="success",
            command=save_expense
        ).pack(pady=15)
        ttk.Button(
            form_frame, text="Back to Expenses", bootstyle="danger",
            command=self.create_expenses_page
        ).pack(pady=5)

    # ------------------------------------------------------------------
    # Import Expenses from CSV
    # ------------------------------------------------------------------
    def import_expenses_csv(self):
        """Create the expense import page."""
        self._clear_parent_frame()

        ttk.Label(
            self.parent_frame,
            text=f"Import Expenses CSV for {self.username}",
            font=("Helvetica", 14, "bold")
        ).pack(pady=15)

        import_frame = ttk.Frame(self.parent_frame, padding=20)
        import_frame.pack(fill="both", expand=True)

        ttk.Label(
            import_frame,
            text="Select CSV file to import your expenses"
        ).pack(anchor="w", pady=5)

        selected_file = StringVar(value="No file selected")
        ttk.Label(import_frame, textvariable=selected_file,
                  foreground="blue").pack(anchor="w", pady=5)

        def open_file_dialog():
            """Open a file dialog to select CSV file."""
            filepath = filedialog.askopenfilename(
                title="Select CSV file",
                filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
            )
            if filepath:
                filename = os.path.basename(filepath)
                selected_file.set(f"Selected file: {filename}")
                import_btn.config(state=NORMAL)
                import_btn.filepath = filepath

        def import_csv():
            """Import selected CSV file into expenses database."""
            filepath = getattr(import_btn, "filepath", None)
            if filepath:
                success, message = self.finance_ops.import_expenses_from_csv(
                    filepath, self.username
                )
                selected_file.set(message)
                if success:
                    import_btn.config(state=DISABLED)

        ttk.Button(
            import_frame, text="Browse...", bootstyle="primary",
            command=open_file_dialog
        ).pack(pady=10)
        import_btn = ttk.Button(
            import_frame, text="Import", bootstyle="success",
            command=import_csv, state=DISABLED
        )
        import_btn.pack(pady=5)
        ttk.Button(
            import_frame, text="Back to Expenses", bootstyle="danger",
            command=self.create_expenses_page
        ).pack(pady=10)

    # ------------------------------------------------------------------
    # View Expenses
    # ------------------------------------------------------------------
    def view_expenses_page(self):
        """Display all recorded expenses."""
        self._clear_parent_frame()

        ttk.Label(
            self.parent_frame,
            text=f"View Expenses for {self.username}",
            font=("Helvetica", 14, "bold")
        ).pack(pady=15)

        expenses = self.finance_ops.get_user_expenses(self.username)
        if not expenses:
            ttk.Label(self.parent_frame, text="No Expenses to view.").pack(pady=10)
            ttk.Button(
                self.parent_frame, text="Back to Expenses", bootstyle="danger",
                command=self.create_expenses_page
            ).pack(pady=5)
            return

        columns = ("ID", "Date", "Category", "Amount", "Description")
        tree = ttk.Treeview(
            self.parent_frame, columns=columns, show="headings", height=10
        )
        tree.pack(pady=10, fill="x")

        for col in columns:
            tree.heading(col, text=col)
            tree.column(
                col,
                anchor="center" if col != "Description" else "w",
                width=10 if col in ["ID", "Date", "Amount"]
                else 25 if col == "Category" else 50
            )

        for exp in expenses:
            # Convert the expenses tuple to a list so we can modify the amount
            exp_list = list(exp)
            # Format the amount (assuming it's at index 3) as US currency
            try:
                amount = float(exp_list[3])
                exp_list[3] = f"${amount:,.2f}"
            except (ValueError, IndexError):
                # If conversion fails, keep original value
                pass
            tree.insert("", "end", values=exp_list)

        ttk.Button(
            self.parent_frame, text="Back to Expenses", bootstyle="danger",
            command=self.create_expenses_page).pack(pady=5)

    # ------------------------------------------------------------------
    # Remove Expenses
    # ------------------------------------------------------------------
    def remove_expenses_page(self):
        """Display a page to remove selected expenses."""
        self._clear_parent_frame()

        ttk.Label(
            self.parent_frame,
            text=f"Remove Expenses for {self.username}",
            font=("Helvetica", 14, "bold")
        ).pack(pady=15)

        expenses = self.finance_ops.get_user_expenses(self.username)
        if not expenses:
            ttk.Label(self.parent_frame, text="No expenses to remove.").pack(pady=10)
            ttk.Button(
                self.parent_frame, text="Back to Expenses", bootstyle="danger",
                command=self.create_expenses_page
            ).pack(pady=5)
            return

        columns = ("ID", "Date", "Category", "Amount", "Description")
        tree = ttk.Treeview(
            self.parent_frame, columns=columns, show="headings", height=10
        )
        tree.pack(pady=10, fill="x")

        for col in columns:
            tree.heading(col, text=col)
            tree.column(
                col,
                anchor="center" if col != "Description" else "w",
                width=10 if col in ["ID", "Date", "Amount"]
                else 25 if col == "Category" else 50
            )

        for exp in expenses:
            tree.insert("", "end", values=exp)

        def delete_selected():
            """Delete the selected expense from database and tree."""
            selected = tree.selection()
            if not selected:
                Messagebox.show_error("Please select an expense to delete.", "Error")
                return

            item = tree.item(selected[0])["values"]
            expense_id = item[0]
            response = Messagebox.okcancel(
                f"Delete expense: {item[0]} (${float(item[3]):.2f}) "
                f"in {item[2]} from {item[1]}?", "Confirm Delete"
            )
            if response != "OK":
                return

            success, message = self.finance_ops.delete_expense(expense_id)
            if success:
                tree.delete(selected[0])
                Messagebox.show_info(message, "Success")
            else:
                Messagebox.show_error(message, "Error")

        ttk.Button(
            self.parent_frame, text="Delete Selected Expense",
            command=delete_selected, bootstyle="danger"
        ).pack(pady=5)
        ttk.Button(
            self.parent_frame, text="Back to Expenses", bootstyle="danger",
            command=self.create_expenses_page
        ).pack(pady=5)

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
            command=self.create_expenses_page
        ).pack(pady=10)

    # ------------------------------------------------------------------
    # Helper Method
    # ------------------------------------------------------------------
    def _clear_parent_frame(self):
        """Clear all widgets from the parent frame."""
        for widget in self.parent_frame.winfo_children():
            widget.destroy()
