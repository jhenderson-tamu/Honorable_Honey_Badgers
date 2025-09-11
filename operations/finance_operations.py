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
    def get_user_expenses(username: str) -> list[tuple]:
        """
        Get all expenses for a specific user.

        Args:
            username (str): Username to filter expenses by.

        Returns:
            list[tuple]: List of expense records.
        """
        with sql.connect("data/finance.db") as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, date, category, amount, description
                FROM expenses
                WHERE username=?
            """, (username,))
            expenses = cursor.fetchall()
        return expenses

    @staticmethod
    def get_user_income(username: str) -> list[tuple]:
        """
        Get all income records for a specific user.

        Args:
            username (str): Username to filter income by.

        Returns:
            list[tuple]: List of income records.
        """
        with sql.connect("data/finance.db") as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, date, category, amount, description
                FROM income
                WHERE username=?
            """, (username,))
            income = cursor.fetchall()
        return income

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
    def import_expenses_from_csv(filepath: str, username: str) -> tuple[bool, str]:
        """
        Import expenses from a CSV file.

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

            with sql.connect("data/finance.db") as conn:
                cursor = conn.cursor()
                for _, row in df.iterrows():
                    cursor.execute("""
                        INSERT INTO expenses (date, category, amount, description, username)
                        VALUES (?, ?, ?, ?, ?)
                    """, (
                        row["date"],
                        row["category"],
                        float(row["amount"]),
                        row.get("description", ""),
                        username
                    ))
                conn.commit()
            return True, "File imported successfully!"
        except Exception as e:
            return False, f"Error importing file: {e}"

    @staticmethod
    def import_income_from_csv(filepath: str, username: str) -> tuple[bool, str]:
        """
        Import income records from a CSV file.

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

            with sql.connect("data/finance.db") as conn:
                cursor = conn.cursor()
                for _, row in df.iterrows():
                    cursor.execute("""
                        INSERT INTO income (date, category, amount, description, username)
                        VALUES (?, ?, ?, ?, ?)
                    """, (
                        row["date"],
                        row["category"],
                        float(row["amount"]),
                        row.get("description", ""),
                        username
                    ))
                conn.commit()
            return True, "File imported successfully!"
        except Exception as e:
            return False, f"Error importing file: {e}"

    # ------------------------------
    # Budget Summary
    # ------------------------------

    @staticmethod
    def get_budget_summary(username: str,
                           start_date: str,
                           end_date: str) -> tuple[float, float, float]:
        """
        Calculate total expenses, income, and leftover funds
        for a user over a date range.

        Args:
            username (str): Username to filter data by.
            start_date (str): Start date (YYYY-MM-DD).
            end_date (str): End date (YYYY-MM-DD).

        Returns:
            tuple[float, float, float]: (total_expenses, total_income, leftover)
        """
        with sql.connect("data/finance.db") as conn:
            cursor = conn.cursor()

            cursor.execute("""
                SELECT COALESCE(SUM(amount), 0)
                FROM expenses
                WHERE username=? AND date BETWEEN ? AND ?
            """, (username, start_date, end_date))
            total_expenses = cursor.fetchone()[0]

            cursor.execute("""
                SELECT COALESCE(SUM(amount), 0)
                FROM income
                WHERE username=? AND date BETWEEN ? AND ?
            """, (username, start_date, end_date))
            total_income = cursor.fetchone()[0]

        leftover = total_income - total_expenses
        return total_expenses, total_income, leftover
