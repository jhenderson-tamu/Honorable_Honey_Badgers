# PROGRAM: Category Management Page
# PURPOSE: Provide a user interface for viewing, updating, and deleting
#          categories for both expenses and income, with safe reassignment
#          when categories are in use.
# INPUT:
#   - parent_frame (Frame): Tkinter frame where page content is rendered.
#   - back_callback (function): Callback to return to the previous page.
# PROCESS:
#   - Display lists of expense and income categories.
#   - Allow renaming of categories (including updates to transactions).
#   - Allow safe deletion of categories, with reassignment of related
#     records to a replacement category.
# OUTPUT:
#   - GUI page for managing expense and income categories, with update
#     and delete operations.
# HONOR CODE: On my honor, as an Aggie, I have neither given nor
#             received unauthorized aid on this academic work.

import tkinter as tk
import ttkbootstrap as ttk
from tkinter import simpledialog, messagebox
from operations.finance_operations import FinanceOperations


class CategoryManager:
    """GUI page for managing expense and income categories."""

    def __init__(self, parent_frame, back_callback):
        """
        Initialize the Category Manager page.

        Args:
            parent_frame (Frame): The tkinter frame used to render this page.
            back_callback (function): Function to call when exiting the page.
        """
        self.parent_frame = parent_frame
        self.back_callback = back_callback
        self.expense_listbox = None
        self.income_listbox = None

    # ------------------------------------------------------------------
    # Page Builder
    # ------------------------------------------------------------------
    def create_category_page(self):
        """Build and display the category management page."""
        # Clear existing widgets
        for w in self.parent_frame.winfo_children():
            w.destroy()

        frame = ttk.Frame(self.parent_frame)
        frame.pack(fill="both", expand=True, padx=20, pady=20)

        # Expense Categories
        ttk.Label(
            frame, text="Expense Categories",
            font=("Helvetica", 14, "bold")
        ).pack(pady=5)
        self.expense_listbox = self._build_listbox(
            frame, FinanceOperations.load_expense_categories()
        )

        # Income Categories
        ttk.Label(
            frame, text="Income Categories",
            font=("Helvetica", 14, "bold")
        ).pack(pady=5)
        self.income_listbox = self._build_listbox(
            frame, FinanceOperations.load_income_categories()
        )

        # Close button (matches other pages)
        ttk.Button(
            frame, text="Close Category Page",
            command=self.back_callback,
            bootstyle="secondary"
        ).pack(pady=10)

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------
    def _build_listbox(self, frame, categories):
        """
        Create a listbox for categories with Update/Delete buttons.

        Args:
            frame (Frame): Parent frame.
            categories (list): Categories to populate listbox.

        Returns:
            tk.Listbox: The populated listbox widget.
        """
        listbox = tk.Listbox(frame, height=8, width=30)
        listbox.pack(pady=5)

        for c in categories:
            listbox.insert("end", c)

        button_frame = ttk.Frame(frame)
        button_frame.pack(pady=2)

        ttk.Button(
            button_frame, text="Update",
            command=lambda lb=listbox: self._update_category(lb),
            bootstyle="info"
        ).pack(side="left", padx=5)

        ttk.Button(
            button_frame, text="Delete",
            command=lambda lb=listbox: self._delete_category(lb),
            bootstyle="danger"
        ).pack(side="left", padx=5)

        return listbox

    def _update_category(self, listbox):
        """
        Handle category renaming.

        Prompts the user for a new name and updates all related
        transactions.

        Args:
            listbox (tk.Listbox): Listbox where the category is selected.
        """
        if not listbox.curselection():
            return

        old = listbox.get(listbox.curselection())
        new = simpledialog.askstring(
            "Update Category", f"Rename '{old}' to:"
        )

        if new:
            if listbox == self.expense_listbox:
                FinanceOperations.update_expense_category(old, new)
            else:
                FinanceOperations.update_income_category(old, new)

            messagebox.showinfo(
                "Updated", f"Category '{old}' renamed to '{new}'"
            )
            self.create_category_page()  # refresh

    def _delete_category(self, listbox):
        """
        Handle category deletion.

        If category is in use, prompts reassignment to another category
        (or defaults to 'Uncategorized').

        Args:
            listbox (tk.Listbox): Listbox where the category is selected.
        """
        if not listbox.curselection():
            return

        cat = listbox.get(listbox.curselection())

        # Check usage count
        if listbox == self.expense_listbox:
            usage_count = FinanceOperations.count_expenses_in_category(cat)
        else:
            usage_count = FinanceOperations.count_income_in_category(cat)

        if usage_count > 0:
            # Prompt reassignment if category is in use
            messagebox.showwarning(
                "Category In Use",
                f"Category '{cat}' is used in {usage_count} record(s).\n"
                "You must reassign those records before deleting."
            )

            new_cat = simpledialog.askstring(
                "Reassign Category",
                f"Enter a new category to reassign {usage_count} record(s)\n"
                f"from '{cat}' to (leave blank for 'Uncategorized'):"
            )

            if not new_cat:
                new_cat = "Uncategorized"

            if listbox == self.expense_listbox:
                FinanceOperations.reassign_or_delete_expense_category(
                    cat, new_cat
                )
            else:
                FinanceOperations.reassign_or_delete_income_category(
                    cat, new_cat
                )

            messagebox.showinfo(
                "Deleted",
                f"Category '{cat}' deleted and reassigned to '{new_cat}'"
            )
        else:
            # Safe delete
            if messagebox.askyesno(
                "Delete", f"Delete category '{cat}'?"
            ):
                if listbox == self.expense_listbox:
                    FinanceOperations.reassign_or_delete_expense_category(cat)
                else:
                    FinanceOperations.reassign_or_delete_income_category(cat)

                messagebox.showinfo(
                    "Deleted", f"Category '{cat}' deleted"
                )

        # Refresh page after action
        self.create_category_page()
