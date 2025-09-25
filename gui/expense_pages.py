# PROGRAM: Expense Management Pages
# PURPOSE: Provide a full set of GUI pages for managing expenses,
#          including adding, importing, viewing, and removing user
#          expenses, along with category management.
# INPUT:
#   - username (str): Username of the logged-in user.
#   - parent_frame (tk.Frame): The frame container where expense pages
#     will be displayed.
# PROCESS:
#   - Builds GUI pages to allow expense management.
#   - Supports manual entry of expenses with category selection or creation.
#   - Allows importing expenses from CSV files.
#   - Displays all recorded expenses in a table with formatted values.
#   - Allows deleting individual expense records with confirmation.
#   - Interacts with FinanceOperations for all database transactions.
# OUTPUT:
#   - User-entered expenses saved to the database.
#   - Imported expenses added from CSV files.
#   - Expense tables displayed in the GUI.
#   - Success or error messages shown in the interface.
# HONOR CODE: On my honor, as an Aggie, I have neither given nor
#             received unauthorized aid on this academic work.

import tkinter as tk
import ttkbootstrap as ttk
from ttkbootstrap.constants import NORMAL, DISABLED
from ttkbootstrap.dialogs import Messagebox
from tkinter import filedialog, StringVar
from datetime import datetime
import os
from operations.finance_operations import FinanceOperations


class ExpensePages:
    """Class to handle expense-related GUI pages."""

    def __init__(self, username: str, parent_frame):
        """
        Initialize ExpensePages.

        Args:
            username (str): Username of the logged-in user.
            parent_frame (tk.Frame): Frame where expense pages will be displayed.
        """
        self.username = username
        self.parent_frame = parent_frame
        self.finance_ops = FinanceOperations()

    # ------------------------------------------------------------------
    # Main Expense Menu
    # ------------------------------------------------------------------
    def create_expenses_page(self):
        """
        Build and display the main expenses menu.

        Features:
            - Manual entry of expenses.
            - Importing expenses from CSV.
            - Viewing all expenses in a table.
            - Removing selected expenses.
        """
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
        """
        Create the manual expense entry page.

        Features:
            - Input fields for description, amount, date, and category.
            - Category dropdown with option to add a new category.
            - Buttons to add category, save expense, or go back.
            - Validation for required fields and amount format.
        """
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
            """Show a notification message for 3 seconds."""
            color = {"info": "green", "error": "red"}.get(type, "black")
            notification_label.config(text=message, foreground=color)
            notification_label.after(3000, lambda: notification_label.config(text=""))

        def add_category():
            """Add a new expense category and update dropdown list."""
            new_cat = new_category_entry.get().strip()
            if not new_cat:
                show_notification("Category name cannot be empty.", "error")
                return

            success, message = self.finance_ops.add_expense_category(new_cat)
            show_notification(message, "info" if success else "error")

            if success:
                new_category_entry.delete(0, "end")
                category_menu.config(values=self.finance_ops.load_expense_categories())
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
        ttk.Button(form_frame, text="Add Category", bootstyle="info", command=add_category).pack(pady=5)
        ttk.Button(form_frame, text="Save Expense", bootstyle="success", command=save_expense).pack(pady=15)
        ttk.Button(form_frame, text="Back to Expenses", bootstyle="danger", command=self.create_expenses_page).pack(pady=5)

    # ------------------------------------------------------------------
    # Import Expenses from CSV
    # ------------------------------------------------------------------
    def import_expenses_csv(self):
        """
        Create the expense import page.

        Features:
            - File browser to select CSV file.
            - Imports expense records into the database.
            - Displays success or error messages after import.
        """
        self._clear_parent_frame()

        ttk.Label(
            self.parent_frame,
            text=f"Import Expenses CSV for {self.username}",
            font=("Helvetica", 14, "bold")
        ).pack(pady=15)

        import_frame = ttk.Frame(self.parent_frame, padding=20)
        import_frame.pack(fill="both", expand=True)

        ttk.Label(import_frame, text="Select CSV file to import your expenses").pack(anchor="w", pady=5)

        selected_file = StringVar(value="No file selected")
        ttk.Label(import_frame, textvariable=selected_file, foreground="blue").pack(anchor="w", pady=5)

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
                success, message = self.finance_ops.import_expenses_from_csv(filepath, self.username)
                selected_file.set(message)
                if success:
                    import_btn.config(state=DISABLED)

        ttk.Button(import_frame, text="Browse...", bootstyle="primary", command=open_file_dialog).pack(pady=10)
        import_btn = ttk.Button(import_frame, text="Import", bootstyle="success", command=import_csv, state=DISABLED)
        import_btn.pack(pady=5)
        ttk.Button(import_frame, text="Back to Expenses", bootstyle="danger", command=self.create_expenses_page).pack(pady=10)

    # ------------------------------------------------------------------
    # View Expenses
    # ------------------------------------------------------------------
    def view_expenses_page(self):
        """
        Display all recorded expenses in a tabular format.

        Features:
            - Shows columns: ID, Date, Category, Amount, Description.
            - Formats amount as currency.
            - Provides a back button to return to menu.
        """
        self._clear_parent_frame()

        ttk.Label(
            self.parent_frame,
            text=f"View Expenses for {self.username}",
            font=("Helvetica", 14, "bold")
        ).pack(pady=15)

        expenses = self.finance_ops.get_user_expenses(self.username)
        if not expenses:
            ttk.Label(self.parent_frame, text="No Expenses to view.").pack(pady=10)
            ttk.Button(self.parent_frame, text="Back to Expenses", bootstyle="danger", command=self.create_expenses_page).pack(pady=5)
            return

        columns = ("ID", "Date", "Category", "Amount", "Description")
        tree = ttk.Treeview(self.parent_frame, columns=columns, show="headings", height=10)
        tree.pack(pady=10, fill="x")

        for col in columns:
            tree.heading(col, text=col)
            tree.column(
                col,
                anchor="center" if col != "Description" else "w",
                width=10 if col in ["ID", "Date", "Amount"] else 25 if col == "Category" else 50
            )

        for exp in expenses:
            exp_list = list(exp)
            try:
                amount = float(exp_list[3])
                exp_list[3] = f"${amount:,.2f}"
            except (ValueError, IndexError):
                pass
            tree.insert("", "end", values=exp_list)

        ttk.Button(self.parent_frame, text="Back to Expenses", bootstyle="danger", command=self.create_expenses_page).pack(pady=5)

    # ------------------------------------------------------------------
    # Remove Expenses
    # ------------------------------------------------------------------
    def remove_expenses_page(self):
        """
        Display a page to remove selected expenses.

        Features:
            - Shows all expenses in a table.
            - Allows selecting a record and deleting it from the database.
            - Confirmation dialog before deletion.
        """
        self._clear_parent_frame()

        ttk.Label(
            self.parent_frame,
            text=f"Remove Expenses for {self.username}",
            font=("Helvetica", 14, "bold")
        ).pack(pady=15)

        expenses = self.finance_ops.get_user_expenses(self.username)
        if not expenses:
            ttk.Label(self.parent_frame, text="No expenses to remove.").pack(pady=10)
            ttk.Button(self.parent_frame, text="Back to Expenses", bootstyle="danger", command=self.create_expenses_page).pack(pady=5)
            return

        columns = ("ID", "Date", "Category", "Amount", "Description")
        tree = ttk.Treeview(self.parent_frame, columns=columns, show="headings", height=10)
        tree.pack(pady=10, fill="x")

        for col in columns:
            tree.heading(col, text=col)
            tree.column(
                col,
                anchor="center" if col != "Description" else "w",
                width=10 if col in ["ID", "Date", "Amount"] else 25 if col == "Category" else 50
            )

        for exp in expenses:
            tree.insert("", "end", values=exp)

        def delete_selected():
            """Delete the selected expense from the database and refresh UI."""
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

        ttk.Button(self.parent_frame, text="Delete Selected Expense", command=delete_selected, bootstyle="danger").pack(pady=5)
        ttk.Button(self.parent_frame, text="Back to Expenses", bootstyle="danger", command=self.create_expenses_page).pack(pady=5)

    # ------------------------------------------------------------------
    # Helper Method
    # ------------------------------------------------------------------
    def _clear_parent_frame(self):
        """Clear all widgets from the parent frame."""
        for widget in self.parent_frame.winfo_children():
            widget.destroy()
