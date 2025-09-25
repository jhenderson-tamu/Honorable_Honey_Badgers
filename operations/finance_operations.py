# PROGRAM: Finance Operations
# PURPOSE: Provide a class with static methods to manage finance-related
# database operations including CRUD for expenses, income, and categories,
# as well as CSV imports and budget summaries.
# INPUT: Various function arguments including dates, descriptions, categories,
# amounts, usernames, and CSV file paths.
# PROCESS: Interacts with the finance SQLite database to insert, update,
# retrieve, and delete financial records.
# OUTPUT: Database modifications and returned results (lists, tuples, or
# status messages).
# HONOR CODE: On my honor, as an Aggie, I have neither given nor received
# unauthorized aid on this academic work.

import sqlite3 as sql
import pandas as pd
from datetime import datetime

class FinanceOperations:
    """Class to handle all finance-related database operations."""

    # ------------------------------
    # Category Operations
    # ------------------------------

    @staticmethod
    def load_expense_categories() -> list[str]:
        """
        Retrieve all expense categories in alphabetical order.

        Returns:
            list[str]: List of expense category names.
        """
        with sql.connect("data/finance.db") as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM expense_category ORDER BY name ASC")
            rows = cursor.fetchall()

        return [row[0] for row in rows]

    @staticmethod
    def load_income_categories() -> list[str]:
        """
        Retrieve all income categories in alphabetical order.

        Returns:
            list[str]: List of income category names.
        """
        with sql.connect("data/finance.db") as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM income_category ORDER BY name ASC")
            rows = cursor.fetchall()

        return [row[0] for row in rows]

    @staticmethod
    def add_expense_category(category_name: str) -> tuple[bool, str]:
        """
        Add a new expense category.

        Args:
            category_name (str): The name of the category to add.

        Returns:
            tuple[bool, str]: (success, message)
        """
        try:
            with sql.connect("data/finance.db") as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT INTO expense_category (name) VALUES (?)",
                    (category_name,)
                )
                conn.commit()
            return True, f"Category '{category_name}' added."
        except sql.IntegrityError:
            return False, f"Category '{category_name}' already exists."

    @staticmethod
    def add_income_category(category_name: str) -> tuple[bool, str]:
        """
        Add a new income category.

        Args:
            category_name (str): The name of the category to add.

        Returns:
            tuple[bool, str]: (success, message)
        """
        try:
            with sql.connect("data/finance.db") as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT INTO income_category (name) VALUES (?)",
                    (category_name,)
                )
                conn.commit()
            return True, f"Category '{category_name}' added."
        except sql.IntegrityError:
            return False, f"Category '{category_name}' already exists."

    # ------------------------------
    # Expense & Income CRUD Operations
    # ------------------------------

    @staticmethod
    def add_expense(date: str, description: str,
                    category: str, amount: float,
                    username: str) -> tuple[bool, str]:
        """
        Add a new expense to the database.

        Args:
            date (str): Date in YYYY-MM-DD format.
            description (str): Expense description.
            category (str): Expense category.
            amount (float): Expense amount.
            username (str): Username associated with expense.

        Returns:
            tuple[bool, str]: (success, message)
        """
        try:
            with sql.connect("data/finance.db") as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO expenses (date, description, category, amount, username)
                    VALUES (?, ?, ?, ?, ?)
                """, (date, description, category, amount, username))
                conn.commit()
            return True, f"Expense added for {username}."
        except Exception as e:
            return False, f"Database error: {e}"

    @staticmethod
    def add_income(date: str, description: str,
                   category: str, amount: float,
                   username: str) -> tuple[bool, str]:
        """
        Add a new income record to the database.

        Args:
            date (str): Date in YYYY-MM-DD format.
            description (str): Income description.
            category (str): Income category.
            amount (float): Income amount.
            username (str): Username associated with income.

        Returns:
            tuple[bool, str]: (success, message)
        """
        try:
            with sql.connect("data/finance.db") as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO income (date, description, category, amount, username)
                    VALUES (?, ?, ?, ?, ?)
                """, (date, description, category, amount, username))
                conn.commit()
            return True, f"Income added for {username}."
        except Exception as e:
            return False, f"Database error: {e}"

    @staticmethod
    def get_user_expenses(username: str):
        """Fetch all expenses for a user, sorted by date descending."""
        import sqlite3 as sql
        with sql.connect("data/finance.db") as conn:
            c = conn.cursor()
            c.execute("""
                SELECT id, date, category, amount, description
                FROM expenses
                WHERE username = ?
                ORDER BY date DESC
            """, (username,))
            return c.fetchall()

    @staticmethod
    def get_user_income(username: str):
        """Fetch all income records for a user, sorted by date descending."""
        import sqlite3 as sql
        with sql.connect("data/finance.db") as conn:
            c = conn.cursor()
            c.execute("""
                SELECT id, date, category, amount, description
                FROM income
                WHERE username = ?
                ORDER BY date DESC
            """, (username,))
            return c.fetchall()

    @staticmethod
    def delete_expense(expense_id: int) -> tuple[bool, str]:
        """
        Delete an expense by its ID.

        Args:
            expense_id (int): Expense record ID.

        Returns:
            tuple[bool, str]: (success, message)
        """
        try:
            with sql.connect("data/finance.db") as conn:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM expenses WHERE id=?", (expense_id,))
                conn.commit()
            return True, "Expense removed successfully!"
        except Exception as e:
            return False, f"Error removing expense: {e}"

    @staticmethod
    def delete_income(income_id: int) -> tuple[bool, str]:
        """
        Delete an income record by its ID.

        Args:
            income_id (int): Income record ID.

        Returns:
            tuple[bool, str]: (success, message)
        """
        try:
            with sql.connect("data/finance.db") as conn:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM income WHERE id=?", (income_id,))
                conn.commit()
            return True, "Income removed successfully!"
        except Exception as e:
            return False, f"Error removing income: {e}"

    # ------------------------------
    # CSV Import Operations
    # ------------------------------

    @staticmethod
    def import_expenses_from_csv(filepath: str, username: str) -> tuple[
        bool, str]:
        """
        Import expenses from a CSV file, automatically adding
        new categories to the expense_category table.

        Args:
            filepath (str): Path to the CSV file.
            username (str): Username to associate with imported expenses.

        Returns:
            tuple[bool, str]: (success, message)
        """
        try:
            df = pd.read_csv(filepath)
            required_cols = {"date", "category", "amount"}

            if not required_cols.issubset(df.columns):
                return False, "CSV is missing required columns (date, category, amount)."

            skipped_rows = 0
            new_categories = set()

            with sql.connect("data/finance.db") as conn:
                cursor = conn.cursor()

                for _, row in df.iterrows():
                    # --- Normalize date ---
                    raw_date = str(row["date"]).strip()
                    date = FinanceOperations.normalize_date(raw_date)
                    if not date:
                        skipped_rows += 1
                        continue  # skip invalid dates

                    # --- Category (default to Uncategorized if blank) ---
                    category = str(row.get("category", "")).strip()
                    if not category:
                        category = "Uncategorized"

                    amount = float(row["amount"])
                    description = str(row.get("description", "")).strip()

                    # --- Ensure category exists ---
                    cursor.execute(
                        "SELECT id FROM expense_category WHERE name = ?",
                        (category,)
                    )
                    if cursor.fetchone() is None:
                        try:
                            cursor.execute(
                                "INSERT INTO expense_category (name) VALUES (?)",
                                (category,)
                            )
                            new_categories.add(category)
                        except sql.IntegrityError:
                            pass

                    # --- Insert expense ---
                    cursor.execute("""
                        INSERT INTO expenses (date, category, amount, description, username)
                        VALUES (?, ?, ?, ?, ?)
                    """, (date, category, amount, description, username))

                conn.commit()

            # Build message
            msg_parts = ["File imported successfully!"]
            if new_categories:
                msg_parts.append(
                    f"Added new categories: {', '.join(sorted(new_categories))}.")
            if skipped_rows > 0:
                msg_parts.append(
                    f"Skipped {skipped_rows} row(s) with invalid dates.")

            return True, " ".join(msg_parts)

        except Exception as e:
            return False, f"Error importing file: {e}"

    @staticmethod
    def import_income_from_csv(filepath: str, username: str) -> tuple[
        bool, str]:
        """
        Import income records from a CSV file, automatically adding
        new categories to the income_category table.

        Args:
            filepath (str): Path to the CSV file.
            username (str): Username to associate with imported income.

        Returns:
            tuple[bool, str]: (success, message)
        """
        try:
            df = pd.read_csv(filepath)
            required_cols = {"date", "category", "amount"}

            if not required_cols.issubset(df.columns):
                return False, "CSV is missing required columns (date, category, amount)."

            skipped_rows = 0
            new_categories = set()

            with sql.connect("data/finance.db") as conn:
                cursor = conn.cursor()

                for _, row in df.iterrows():
                    # --- Normalize date ---
                    raw_date = str(row["date"]).strip()
                    date = FinanceOperations.normalize_date(raw_date)
                    if not date:
                        skipped_rows += 1
                        continue  # skip invalid dates

                    # --- Category (default to Uncategorized if blank) ---
                    category = str(row.get("category", "")).strip()
                    if not category:
                        category = "Uncategorized"

                    amount = float(row["amount"])
                    description = str(row.get("description", "")).strip()

                    # --- Ensure category exists ---
                    cursor.execute(
                        "SELECT id FROM income_category WHERE name = ?",
                        (category,)
                    )
                    if cursor.fetchone() is None:
                        try:
                            cursor.execute(
                                "INSERT INTO income_category (name) VALUES (?)",
                                (category,)
                            )
                            new_categories.add(category)
                        except sql.IntegrityError:
                            pass

                    # --- Insert income ---
                    cursor.execute("""
                        INSERT INTO income (date, category, amount, description, username)
                        VALUES (?, ?, ?, ?, ?)
                    """, (date, category, amount, description, username))

                conn.commit()

            # Build message
            msg_parts = ["File imported successfully!"]
            if new_categories:
                msg_parts.append(
                    f"Added new categories: {', '.join(sorted(new_categories))}.")
            if skipped_rows > 0:
                msg_parts.append(
                    f"Skipped {skipped_rows} row(s) with invalid dates.")

            return True, " ".join(msg_parts)

        except Exception as e:
            return False, f"Error importing file: {e}"

    @staticmethod
    def normalize_date(date_str: str) -> str | None:
        """
        Normalize dates to YYYY-MM-DD format.
        Returns None if the date cannot be parsed.
        """
        try:
            parsed = pd.to_datetime(date_str, errors="coerce")
            if pd.notna(parsed):
                return parsed.strftime("%Y-%m-%d")
        except Exception:
            return None
        return None

    # ------------------------------
    # Budget Summary
    # ------------------------------

    @staticmethod
    def get_budget_summary(username: str, start_date: str, end_date: str):
        """
        Calculate total expenses, total income, net savings, and savings transfers
        for a date range.

        - Normal expenses reduce money.
        - 'Savings' category expenses are treated as transfers into savings.
        - Net savings = Income - Normal Expenses + Savings Transfers.
        """
        with sql.connect("data/finance.db") as conn:
            expenses = pd.read_sql_query(
                "SELECT date, category, amount FROM expenses WHERE username = ?",
                conn, params=(username,)
            )
            income = pd.read_sql_query(
                "SELECT date, amount FROM income WHERE username = ?",
                conn, params=(username,)
            )

        # Convert to datetime
        for df in [expenses, income]:
            if not df.empty:
                df["date"] = pd.to_datetime(df["date"], errors="coerce")

        start_date = pd.to_datetime(start_date)
        end_date = pd.to_datetime(end_date)

        # Filter by date range
        if not expenses.empty:
            expenses = expenses[(expenses["date"] >= start_date) & (expenses["date"] <= end_date)]
        if not income.empty:
            income = income[(income["date"] >= start_date) & (income["date"] <= end_date)]

        # Separate savings from normal expenses
        if not expenses.empty:
            savings_transfers = expenses.loc[expenses["category"].str.lower() == "savings", "amount"].sum()
            normal_expenses = expenses.loc[expenses["category"].str.lower() != "savings", "amount"].sum()
        else:
            savings_transfers = 0.0
            normal_expenses = 0.0

        total_income = income["amount"].sum() if not income.empty else 0.0
        total_expenses = normal_expenses
        net_savings = total_income - normal_expenses + savings_transfers

        return total_expenses, total_income, net_savings, savings_transfers

    # ------------------------------
    # Expense & Income Category Management
    # ------------------------------

# ----- Expense Category -----
    @staticmethod
    def update_expense_category(old_name, new_name):
        """Update an expense category and reassign all expenses."""
        conn = sql.connect("data/finance.db")
        cursor = conn.cursor()

        # Update category table
        cursor.execute(
            "UPDATE expense_category SET name = ? WHERE name = ?",
            (new_name, old_name)
        )

        # Update existing expenses
        cursor.execute(
            "UPDATE expenses SET category = ? WHERE category = ?",
            (new_name, old_name)
        )

        conn.commit()
        conn.close()

    @staticmethod
    def reassign_or_delete_expense_category(old_cat, new_cat="Uncategorized"):
        """Reassign expenses to a new category and delete the old one."""
        conn = sql.connect("data/finance.db")
        cursor = conn.cursor()

        # Ensure new category exists
        cursor.execute("INSERT OR IGNORE INTO expense_category (name) VALUES (?)", (new_cat,))

        # Reassign expenses
        cursor.execute(
            "UPDATE expenses SET category = ? WHERE category = ?",
            (new_cat, old_cat)
        )

        # Remove old category
        cursor.execute("DELETE FROM expense_category WHERE name = ?", (old_cat,))

        conn.commit()
        conn.close()

    @staticmethod
    def count_expenses_in_category(category_name):
        """Return how many expenses use a given category."""
        conn = sql.connect("data/finance.db")
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM expenses WHERE category = ?",
                       (category_name,))
        count = cursor.fetchone()[0]
        conn.close()
        return count

    # ----- Income Category -----
    @staticmethod
    def update_income_category(old_name, new_name):
        """Update an income category and reassign all income records."""
        conn = sql.connect("data/finance.db")
        cursor = conn.cursor()

        # Update category table
        cursor.execute(
            "UPDATE income_category SET name = ? WHERE name = ?",
            (new_name, old_name)
        )

        # Update existing income records
        cursor.execute(
            "UPDATE income SET category = ? WHERE category = ?",
            (new_name, old_name)
        )

        conn.commit()
        conn.close()

    @staticmethod
    def reassign_or_delete_income_category(old_cat, new_cat="Uncategorized"):
        """Reassign income records to a new category and delete the old one."""
        conn = sql.connect("data/finance.db")
        cursor = conn.cursor()

        # Ensure new category exists
        cursor.execute("INSERT OR IGNORE INTO income_category (name) VALUES (?)", (new_cat,))

        # Reassign income
        cursor.execute(
            "UPDATE income SET category = ? WHERE category = ?",
            (new_cat, old_cat)
        )

        # Remove old category
        cursor.execute("DELETE FROM income_category WHERE name = ?", (old_cat,))

        conn.commit()
        conn.close()

    @staticmethod
    def count_income_in_category(category_name):
        """Return how many income records use a given category."""
        conn = sql.connect("data/finance.db")
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM income WHERE category = ?",
                       (category_name,))
        count = cursor.fetchone()[0]
        conn.close()
        return count