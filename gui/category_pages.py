# PROGRAM: Category Management Page
# PURPOSE: Allow users to view, update, and delete categories
# for both expenses and income, with safe reassignment.
# INPUT: Parent frame from main_app, and a back callback function
# OUTPUT: GUI interface for managing categories

import tkinter as tk
import ttkbootstrap as ttk
from tkinter import simpledialog, messagebox
from operations.finance_operations import FinanceOperations


class CategoryManager:
    """GUI page for managing expense and income categories."""

    def __init__(self, parent_frame, back_callback):
        """
        Initialize category manager.

        Args:
            parent_frame (tk.Frame): The frame to display content inside.
            back_callback (function): Function to call when closing the page.
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
        for w in self.parent_frame.winfo_children():
            w.destroy()

        frame = ttk.Frame(self.parent_frame)
        frame.pack(fill="both", expand=True, padx=20, pady=20)

        # Expense Categories
        ttk.Label(frame, text="Expense Categories",
                  font=("Helvetica", 14, "bold")).pack(pady=5)
        self.expense_listbox = self._build_listbox(
            frame, FinanceOperations.load_expense_categories())

        # Income Categories
        ttk.Label(frame, text="Income Categories",
                  font=("Helvetica", 14, "bold")).pack(pady=5)
        self.income_listbox = self._build_listbox(
            frame, FinanceOperations.load_income_categories())

        # Close button (matches other pages)
        ttk.Button(frame, text="Close Category Page",
                   command=self.back_callback,
                   bootstyle="secondary").pack(pady=10)

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------
    def _build_listbox(self, frame, categories):
        """Create a listbox with update/delete buttons."""
        listbox = tk.Listbox(frame, height=8, width=30)
        listbox.pack(pady=5)
        for c in categories:
            listbox.insert("end", c)

        button_frame = ttk.Frame(frame)
        button_frame.pack(pady=2)

        ttk.Button(button_frame, text="Update",
                   command=lambda lb=listbox: self._update_category(lb),
                   bootstyle="info").pack(side="left", padx=5)
        ttk.Button(button_frame, text="Delete",
                   command=lambda lb=listbox: self._delete_category(lb),
                   bootstyle="danger").pack(side="left", padx=5)
        return listbox

    def _update_category(self, listbox):
        """Handle category rename (also updates transactions)."""
        if not listbox.curselection():
            return
        old = listbox.get(listbox.curselection())
        new = simpledialog.askstring("Update Category", f"Rename '{old}' to:")
        if new:
            if listbox == self.expense_listbox:
                FinanceOperations.update_expense_category(old, new)
            else:
                FinanceOperations.update_income_category(old, new)
            messagebox.showinfo("Updated", f"Category '{old}' renamed to '{new}'")
            self.create_category_page()  # refresh

    def _delete_category(self, listbox):
        """Handle category deletion with usage check and reassignment."""
        if not listbox.curselection():
            return

        cat = listbox.get(listbox.curselection())

        # Check usage
        if listbox == self.expense_listbox:
            usage_count = FinanceOperations.count_expenses_in_category(cat)
        else:
            usage_count = FinanceOperations.count_income_in_category(cat)

        if usage_count > 0:
            # Warn + prompt reassignment
            messagebox.showwarning(
                "Category In Use",
                f"Category '{cat}' is currently used in {usage_count} record(s).\n"
                f"You must reassign those records before deleting."
            )

            new_cat = simpledialog.askstring(
                "Reassign Category",
                f"Enter a new category to reassign {usage_count} record(s)\n"
                f"from '{cat}' to (leave blank for 'Uncategorized'):"
            )

            if not new_cat:
                new_cat = "Uncategorized"

            if listbox == self.expense_listbox:
                FinanceOperations.reassign_or_delete_expense_category(cat, new_cat)
            else:
                FinanceOperations.reassign_or_delete_income_category(cat, new_cat)

            messagebox.showinfo(
                "Deleted",
                f"Category '{cat}' deleted and reassigned to '{new_cat}'"
            )
        else:
            # Safe to delete immediately
            if messagebox.askyesno("Delete", f"Delete category '{cat}'?"):
                if listbox == self.expense_listbox:
                    FinanceOperations.reassign_or_delete_expense_category(cat)
                else:
                    FinanceOperations.reassign_or_delete_income_category(cat)

                messagebox.showinfo("Deleted", f"Category '{cat}' deleted")

        # Refresh page
        self.create_category_page()
