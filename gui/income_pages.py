# PROGRAM: Income Management Pages
# PURPOSE: Provide pages for adding, importing, viewing, and removing
# user income records, including category management.
# INPUT: Username of the logged-in user and the parent frame for display.
# PROCESS: Creates GUI pages to manage income data, interacts with
# FinanceOperations for data storage/retrieval, and updates the interface.
# OUTPUT: User-entered income saved to database, displayed income tables,
# or success/error messages in the GUI.
# HONOR CODE: On my honor, as an Aggie, I have neither given nor
# received unauthorized aid on this academic work.

import tkinter as tk
import ttkbootstrap as ttk
from ttkbootstrap.constants import NORMAL, DISABLED
from ttkbootstrap.dialogs import Messagebox
from tkinter import filedialog, StringVar
from datetime import datetime
import os
from operations.finance_operations import FinanceOperations


class IncomePages:
    """Class to handle income-related GUI pages."""

    def __init__(self, username: str, parent_frame):
        """
        Initialize IncomePages.

        Args:
            username (str): Username of the logged-in user.
            parent_frame: The frame where income pages will be displayed.
        """
        self.username = username
        self.parent_frame = parent_frame
        self.finance_ops = FinanceOperations()

    # ------------------------------------------------------------------
    # Main Income Menu
    # ------------------------------------------------------------------
    def create_income_page(self):
        """Create the main income menu with available options."""
        self._clear_parent_frame()

        ttk.Label(
            self.parent_frame,
            text=f"Income Options for {self.username}",
            font=("Helvetica", 14, "bold")
        ).pack(pady=15)

        frame = ttk.Frame(self.parent_frame, padding=20)
        frame.pack(fill="both", expand=True)

        ttk.Button(
            frame, text="Income Manual Entry", bootstyle="primary", width=20,
            command=self.income_entry_page
        ).pack(pady=10)

        ttk.Button(
            frame, text="Import Income", bootstyle="primary", width=20,
            command=self.import_income_csv
        ).pack(pady=10)

        ttk.Button(
            frame, text="View Income", bootstyle="primary", width=20,
            command=self.view_income_page
        ).pack(pady=10)

        ttk.Button(
            frame, text="Remove Income", bootstyle="primary", width=20,
            command=self.remove_income_page
        ).pack(pady=10)

        ttk.Button(
            frame, text="Close Income Page", bootstyle="danger", width=20,
            command=self.close_income_page
        ).pack(pady=20)

    def close_income_page(self):
        """Close the income page by clearing all widgets."""
        self._clear_parent_frame()

    # ------------------------------------------------------------------
    # Income Entry Page
    # ------------------------------------------------------------------
    def income_entry_page(self):
        """Create the manual income entry page."""
        self._clear_parent_frame()

        ttk.Label(
            self.parent_frame,
            text=f"Manual Income Entry for {self.username}",
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
            values=self.finance_ops.load_income_categories(),
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
            """Display a temporary notification message."""
            color = {"info": "green", "error": "red"}.get(type, "black")
            notification_label.config(text=message, foreground=color)
            notification_label.after(
                3000, lambda: notification_label.config(text="")
            )

        def add_category():
            """Add a new income category to the database."""
            new_cat = new_category_entry.get().strip()
            if not new_cat:
                show_notification("Category name cannot be empty.", "error")
                return

            success, message = self.finance_ops.add_income_category(new_cat)
            show_notification(message, "info" if success else "error")

            if success:
                new_category_entry.delete(0, "end")
                category_menu.config(
                    values=self.finance_ops.load_income_categories()
                )
                category_var.set(new_cat)

        def save_income():
            """Validate and save the income entry to the database."""
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

            success, message = self.finance_ops.add_income(
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
            form_frame, text="Save Income", bootstyle="success",
            command=save_income
        ).pack(pady=15)
        ttk.Button(
            form_frame, text="Back to Income", bootstyle="danger",
            command=self.create_income_page
        ).pack(pady=10)

    # ------------------------------------------------------------------
    # Import Income CSV
    # ------------------------------------------------------------------
    def import_income_csv(self):
        """Create the income import page."""
        self._clear_parent_frame()

        ttk.Label(
            self.parent_frame,
            text=f"Import Income CSV for {self.username}",
            font=("Helvetica", 14, "bold")
        ).pack(pady=15)

        import_frame = ttk.Frame(self.parent_frame, padding=20)
        import_frame.pack(fill="both", expand=True)

        ttk.Label(
            import_frame, text="Select CSV file to import your income"
        ).pack(anchor="w", pady=5)

        selected_file = StringVar(value="No file selected")
        ttk.Label(import_frame, textvariable=selected_file,
                  foreground="blue").pack(anchor="w", pady=5)

        def open_file_dialog():
            """Open file dialog for CSV selection."""
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
            """Import the selected CSV file into the database."""
            filepath = getattr(import_btn, "filepath", None)
            if filepath:
                success, message = self.finance_ops.import_income_from_csv(
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
            import_frame, text="Back to Income", bootstyle="danger",
            command=self.create_income_page
        ).pack(pady=10)

    # ------------------------------------------------------------------
    # View Income
    # ------------------------------------------------------------------
    def view_income_page(self):
        """Display all recorded income entries."""
        self._clear_parent_frame()

        ttk.Label(
            self.parent_frame,
            text=f"View Income for {self.username}",
            font=("Helvetica", 14, "bold")
        ).pack(pady=15)

        income = self.finance_ops.get_user_income(self.username)
        if not income:
            ttk.Label(self.parent_frame, text="No Income to view.").pack(pady=10)
            ttk.Button(
                self.parent_frame, text="Back to Income", bootstyle="danger",
                command=self.create_income_page
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

        for inc in income:
            tree.insert("", "end", values=inc)

        ttk.Button(
            self.parent_frame, text="Back to Income", bootstyle="danger",
            command=self.create_income_page
        ).pack(pady=5)

    # ------------------------------------------------------------------
    # Remove Income
    # ------------------------------------------------------------------
    def remove_income_page(self):
        """Display a page to remove selected income records."""
        self._clear_parent_frame()

        ttk.Label(
            self.parent_frame,
            text=f"Remove Income for {self.username}",
            font=("Helvetica", 14, "bold")
        ).pack(pady=15)

        income = self.finance_ops.get_user_income(self.username)
        if not income:
            ttk.Label(self.parent_frame, text="No Income to remove.").pack(pady=10)
            ttk.Button(
                self.parent_frame, text="Back to Income", bootstyle="danger",
                command=self.create_income_page
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

        for inc in income:
            tree.insert("", "end", values=inc)

        def delete_selected():
            """Delete the selected income record."""
            selected = tree.selection()
            if not selected:
                Messagebox.show_error("Please select an income to delete.", "Error")
                return

            item = tree.item(selected[0])["values"]
            income_id = item[0]

            response = Messagebox.okcancel(
                f"Delete income: {item[0]} (${float(item[3]):.2f}) "
                f"in {item[2]} from {item[1]}?",
                "Confirm Delete"
            )
            if response != "OK":
                return

            success, message = self.finance_ops.delete_income(income_id)
            if success:
                tree.delete(selected[0])
                Messagebox.show_info(message, "Success")
            else:
                Messagebox.show_error(message, "Error")

        ttk.Button(
            self.parent_frame, text="Delete Selected Income",
            command=delete_selected, bootstyle="danger"
        ).pack(pady=5)
        ttk.Button(
            self.parent_frame, text="Back to Income", bootstyle="danger",
            command=self.create_income_page
        ).pack(pady=5)

    # ------------------------------------------------------------------
    # Helper Method
    # ------------------------------------------------------------------
    def _clear_parent_frame(self):
        """Clear all widgets from the parent frame."""
        for widget in self.parent_frame.winfo_children():
            widget.destroy()
