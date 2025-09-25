# PROGRAM: Finance Operations
# PURPOSE:
#   Provide a class with static methods to manage finance-related
#   database operations. Includes CRUD functionality for expenses,
#   income, and categories, CSV import functionality, and budget
#   summary calculations.
# INPUT:
#   - Function arguments such as dates, descriptions, categories,
#     amounts, usernames, and CSV file paths.
# PROCESS:
#   - Connects to the SQLite database (`finance.db`) to insert,
#     update, retrieve, and delete records.
#   - Normalizes dates and validates input before saving.
#   - Imports CSV files into the database with automatic category
#     handling.
#   - Computes summaries for budget reports.
# OUTPUT:
#   - Database changes (insert, update, delete).
#   - Retrieved results (lists, tuples, or DataFrames).
#   - Success/error messages returned as tuples.
# HONOR CODE:
#   On my honor, as an Aggie, I have neither given nor received
#   unauthorized aid on this academic work.

import sqlite3 as sql
import pandas as pd


class FinanceOperations:
    """Class containing static methods to handle finance-related
    database operations."""

    # ------------------------------------------------------------------
    # Category Operations
    # ------------------------------------------------------------------

    @staticmethod
    def load_expense_categories() -> list[str]:
        """
        Retrieve all expense categories in alphabetical order.

        Returns:
            list[str]: List of expense category names.
        """
        with sql.connect("data/finance.db") as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT name FROM expense_category ORDER BY name ASC"
            )
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
            cursor.execute(
                "SELECT name FROM income_category ORDER BY name ASC"
            )
            rows = cursor.fetchall()
        return [row[0] for row in rows]

    @staticmethod
    def add_expense_category(category_name: str) -> tuple[bool, str]:
        """
        Insert a new expense category into the database.

        Args:
            category_name (str): Category name to add.

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
        Insert a new income category into the database.

        Args:
            category_name (str): Category name to add.

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

    # ------------------------------------------------------------------
    # Expense & Income CRUD Operations
    # ------------------------------------------------------------------

    @staticmethod
    def add_expense(date: str, description: str,
                    category: str, amount: float,
                    username: str) -> tuple[bool, str]:
        """
        Add a new expense record.

        Args:
            date (str): Date in YYYY-MM-DD format.
            description (str): Expense description.
            category (str): Expense category.
            amount (float): Expense amount.
            username (str): Username linked to the expense.

        Returns:
            tuple[bool, str]: (success, message)
        """
        try:
            with sql.connect("data/finance.db") as conn:
                cursor = conn.cursor()
                cursor.execute(
                    """
                    INSERT INTO expenses
                    (date, description, category, amount, username)
                    VALUES (?, ?, ?, ?, ?)
                    """,
                    (date, description, category, amount, username)
                )
                conn.commit()
            return True, f"Expense added for {username}."
        except Exception as e:
            return False, f"Database error: {e}"

    @staticmethod
    def add_income(date: str, description: str,
                   category: str, amount: float,
                   username: str) -> tuple[bool, str]:
        """
        Add a new income record.

        Args:
            date (str): Date in YYYY-MM-DD format.
            description (str): Income description.
            category (str): Income category.
            amount (float): Income amount.
            username (str): Username linked to the income.

        Returns:
            tuple[bool, str]: (success, message)
        """
        try:
            with sql.connect("data/finance.db") as conn:
                cursor = conn.cursor()
                cursor.execute(
                    """
                    INSERT INTO income
                    (date, description, category, amount, username)
                    VALUES (?, ?, ?, ?, ?)
                    """,
                    (date, description, category, amount, username)
                )
                conn.commit()
            return True, f"Income added for {username}."
        except Exception as e:
            return False, f"Database error: {e}"

    @staticmethod
    def get_user_expenses(username: str):
        """
        Fetch all expenses for a user.

        Args:
            username (str): Username to filter by.

        Returns:
            list[tuple]: List of expenses sorted by date descending.
        """
        with sql.connect("data/finance.db") as conn:
            c = conn.cursor()
            c.execute(
                """
                SELECT id, date, category, amount, description
                FROM expenses
                WHERE username = ?
                ORDER BY date DESC
                """,
                (username,)
            )
            return c.fetchall()

    @staticmethod
    def get_user_income(username: str):
        """
        Fetch all income records for a user.

        Args:
            username (str): Username to filter by.

        Returns:
            list[tuple]: List of income records sorted by date descending.
        """
        with sql.connect("data/finance.db") as conn:
            c = conn.cursor()
            c.execute(
                """
                SELECT id, date, category, amount, description
                FROM income
                WHERE username = ?
                ORDER BY date DESC
                """,
                (username,)
            )
            return c.fetchall()

    @staticmethod
    def delete_expense(expense_id: int) -> tuple[bool, str]:
        """
        Delete an expense record by ID.

        Args:
            expense_id (int): ID of expense to delete.

        Returns:
            tuple[bool, str]: (success, message)
        """
        try:
            with sql.connect("data/finance.db") as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "DELETE FROM expenses WHERE id=?",
                    (expense_id,)
                )
                conn.commit()
            return True, "Expense removed successfully!"
        except Exception as e:
            return False, f"Error removing expense: {e}"

    @staticmethod
    def delete_income(income_id: int) -> tuple[bool, str]:
        """
        Delete an income record by ID.

        Args:
            income_id (int): ID of income to delete.

        Returns:
            tuple[bool, str]: (success, message)
        """
        try:
            with sql.connect("data/finance.db") as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "DELETE FROM income WHERE id=?",
                    (income_id,)
                )
                conn.commit()
            return True, "Income removed successfully!"
        except Exception as e:
            return False, f"Error removing income: {e}"

    # ------------------------------------------------------------------
    # CSV Import Operations
    # ------------------------------------------------------------------

    @staticmethod
    def import_expenses_from_csv(filepath: str,
                                 username: str) -> tuple[bool, str]:
        """
        Import expenses from a CSV file, automatically adding new
        categories to the expense_category table.
        """
        try:
            df = pd.read_csv(filepath)
            required_cols = {"date", "category", "amount"}
            if not required_cols.issubset(df.columns):
                return (False,
                        "CSV missing required columns "
                        "(date, category, amount).")

            skipped_rows = 0
            new_categories = set()
            with sql.connect("data/finance.db") as conn:
                cursor = conn.cursor()
                for _, row in df.iterrows():
                    raw_date = str(row["date"]).strip()
                    date = FinanceOperations.normalize_date(raw_date)
                    if not date:
                        skipped_rows += 1
                        continue

                    category = str(row.get("category", "")).strip()
                    if not category:
                        category = "Uncategorized"

                    amount = float(row["amount"])
                    description = str(row.get("description", "")).strip()

                    cursor.execute(
                        "SELECT id FROM expense_category WHERE name = ?",
                        (category,)
                    )
                    if cursor.fetchone() is None:
                        try:
                            cursor.execute(
                                "INSERT INTO expense_category (name) "
                                "VALUES (?)",
                                (category,)
                            )
                            new_categories.add(category)
                        except sql.IntegrityError:
                            pass

                    cursor.execute(
                        """
                        INSERT INTO expenses
                        (date, category, amount, description, username)
                        VALUES (?, ?, ?, ?, ?)
                        """,
                        (date, category, amount, description, username)
                    )
                conn.commit()

            msg_parts = ["File imported successfully!"]
            if new_categories:
                msg_parts.append(
                    f"Added new categories: "
                    f"{', '.join(sorted(new_categories))}."
                )
            if skipped_rows > 0:
                msg_parts.append(
                    f"Skipped {skipped_rows} row(s) with invalid dates."
                )
            return True, " ".join(msg_parts)

        except Exception as e:
            return False, f"Error importing file: {e}"

    @staticmethod
    def import_income_from_csv(filepath: str,
                               username: str) -> tuple[bool, str]:
        """
        Import income from a CSV file, automatically adding new
        categories to the income_category table.
        """
        try:
            df = pd.read_csv(filepath)
            required_cols = {"date", "category", "amount"}
            if not required_cols.issubset(df.columns):
                return (False,
                        "CSV missing required columns "
                        "(date, category, amount).")

            skipped_rows = 0
            new_categories = set()
            with sql.connect("data/finance.db") as conn:
                cursor = conn.cursor()
                for _, row in df.iterrows():
                    raw_date = str(row["date"]).strip()
                    date = FinanceOperations.normalize_date(raw_date)
                    if not date:
                        skipped_rows += 1
                        continue

                    category = str(row.get("category", "")).strip()
                    if not category:
                        category = "Uncategorized"

                    amount = float(row["amount"])
                    description = str(row.get("description", "")).strip()

                    cursor.execute(
                        "SELECT id FROM income_category WHERE name = ?",
                        (category,)
                    )
                    if cursor.fetchone() is None:
                        try:
                            cursor.execute(
                                "INSERT INTO income_category (name) "
                                "VALUES (?)",
                                (category,)
                            )
                            new_categories.add(category)
                        except sql.IntegrityError:
                            pass

                    cursor.execute(
                        """
                        INSERT INTO income
                        (date, category, amount, description, username)
                        VALUES (?, ?, ?, ?, ?)
                        """,
                        (date, category, amount, description, username)
                    )
                conn.commit()

            msg_parts = ["File imported successfully!"]
            if new_categories:
                msg_parts.append(
                    f"Added new categories: "
                    f"{', '.join(sorted(new_categories))}."
                )
            if skipped_rows > 0:
                msg_parts.append(
                    f"Skipped {skipped_rows} row(s) with invalid dates."
                )
            return True, " ".join(msg_parts)

        except Exception as e:
            return False, f"Error importing file: {e}"

    # ------------------------------------------------------------------
    # Utility Functions
    # ------------------------------------------------------------------

    @staticmethod
    def normalize_date(date_str: str) -> str | None:
        """
        Normalize a date string into YYYY-MM-DD format.

        Returns None if parsing fails.
        """
        try:
            parsed = pd.to_datetime(date_str, errors="coerce")
            if pd.notna(parsed):
                return parsed.strftime("%Y-%m-%d")
        except Exception:
            return None
        return None

    # ------------------------------------------------------------------
    # Budget Summary
    # ------------------------------------------------------------------

    @staticmethod
    def get_budget_summary(username: str,
                           start_date: str,
                           end_date: str):
        """
        Calculate totals for expenses, income, net savings,
        and savings transfers in a date range.
        """
        with sql.connect("data/finance.db") as conn:
            expenses = pd.read_sql_query(
                "SELECT date, category, amount FROM expenses "
                "WHERE username = ?",
                conn, params=(username,)
            )
            income = pd.read_sql_query(
                "SELECT date, amount FROM income WHERE username = ?",
                conn, params=(username,)
            )

        for df in [expenses, income]:
            if not df.empty:
                df["date"] = pd.to_datetime(df["date"], errors="coerce")

        start_date = pd.to_datetime(start_date)
        end_date = pd.to_datetime(end_date)

        if not expenses.empty:
            expenses = expenses[
                (expenses["date"] >= start_date) &
                (expenses["date"] <= end_date)
            ]
        if not income.empty:
            income = income[
                (income["date"] >= start_date) &
                (income["date"] <= end_date)
            ]

        if not expenses.empty:
            savings_transfers = expenses.loc[
                expenses["category"].str.lower() == "savings",
                "amount"
            ].sum()
            normal_expenses = expenses.loc[
                expenses["category"].str.lower() != "savings",
                "amount"
            ].sum()
        else:
            savings_transfers = 0.0
            normal_expenses = 0.0

        total_income = income["amount"].sum() if not income.empty else 0.0
        total_expenses = normal_expenses
        net_savings = total_income - normal_expenses + savings_transfers

        return total_expenses, total_income, net_savings, savings_transfers

    # ------------------------------------------------------------------
    # Category Management
    # ------------------------------------------------------------------

    @staticmethod
    def update_expense_category(old_name: str, new_name: str):
        """Update an expense category and reassign all expenses."""
        conn = sql.connect("data/finance.db")
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE expense_category SET name = ? WHERE name = ?",
            (new_name, old_name)
        )
        cursor.execute(
            "UPDATE expenses SET category = ? WHERE category = ?",
            (new_name, old_name)
        )
        conn.commit()
        conn.close()

    @staticmethod
    def reassign_or_delete_expense_category(old_cat: str,
                                            new_cat: str = "Uncategorized"):
        """Reassign expenses to a new category and delete the old one."""
        conn = sql.connect("data/finance.db")
        cursor = conn.cursor()
        cursor.execute(
            "INSERT OR IGNORE INTO expense_category (name) VALUES (?)",
            (new_cat,)
        )
        cursor.execute(
            "UPDATE expenses SET category = ? WHERE category = ?",
            (new_cat, old_cat)
        )
        cursor.execute(
            "DELETE FROM expense_category WHERE name = ?",
            (old_cat,)
        )
        conn.commit()
        conn.close()

    @staticmethod
    def count_expenses_in_category(category_name: str) -> int:
        """Return how many expenses use a given category."""
        conn = sql.connect("data/finance.db")
        cursor = conn.cursor()
        cursor.execute(
            "SELECT COUNT(*) FROM expenses WHERE category = ?",
            (category_name,)
        )
        count = cursor.fetchone()[0]
        conn.close()
        return count

    @staticmethod
    def update_income_category(old_name: str, new_name: str):
        """Update an income category and reassign all records."""
        conn = sql.connect("data/finance.db")
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE income_category SET name = ? WHERE name = ?",
            (new_name, old_name)
        )
        cursor.execute(
            "UPDATE income SET category = ? WHERE category = ?",
            (new_name, old_name)
        )
        conn.commit()
        conn.close()

    @staticmethod
    def reassign_or_delete_income_category(old_cat: str,
                                           new_cat: str = "Uncategorized"):
        """Reassign income to a new category and delete the old one."""
        conn = sql.connect("data/finance.db")
        cursor = conn.cursor()
        cursor.execute(
            "INSERT OR IGNORE INTO income_category (name) VALUES (?)",
            (new_cat,)
        )
        cursor.execute(
            "UPDATE income SET category = ? WHERE category = ?",
            (new_cat, old_cat)
        )
        cursor.execute(
            "DELETE FROM income_category WHERE name = ?",
            (old_cat,)
        )
        conn.commit()
        conn.close()

    @staticmethod
    def count_income_in_category(category_name: str) -> int:
        """Return how many income records use a given category."""
        conn = sql.connect("data/finance.db")
        cursor = conn.cursor()
        cursor.execute(
            "SELECT COUNT(*) FROM income WHERE category = ?",
            (category_name,)
        )
        count = cursor.fetchone()[0]
        conn.close()
        return count
