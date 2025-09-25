# PROGRAM: Reports Operations
# PURPOSE:
#   Provide functions to access financial data for generating expense
#   and income reports. Queries are returned as pandas DataFrames for
#   easy use in charts and tables.
# INPUT:
#   - Username (str)
#   - Optional date ranges (start_date, end_date) in YYYY-MM-DD format
# PROCESS:
#   - Execute SQL queries against the SQLite finance database
#   - Convert results into pandas DataFrames
#   - Normalize date and amount fields for consistency
# OUTPUT:
#   - DataFrames ready for chart plotting and table display
# HONOR CODE:
#   On my honor, as an Aggie, I have neither given nor received
#   unauthorized aid on this academic work.

import sqlite3 as sql
import pandas as pd


def get_user_expenses_by_category(username: str) -> pd.DataFrame:
    """
    Retrieve expenses grouped by category for a user.

    Used for generating the "Expenses by Category" pie chart.

    Args:
        username (str): The username to filter expenses.

    Returns:
        pd.DataFrame: DataFrame with columns:
            - category (str): Expense category name.
            - total (float): Total amount spent in that category.
    """
    with sql.connect("data/finance.db") as conn:
        df = pd.read_sql_query(
            """
            SELECT category, SUM(amount) AS total
            FROM expenses
            WHERE username=?
            GROUP BY category
            ORDER BY total DESC
            """,
            conn, params=(username,)
        )
    return df


def get_user_expenses_range(username: str,
                            start_date: str,
                            end_date: str) -> pd.DataFrame:
    """
    Retrieve all expenses for a user within a date range.

    Args:
        username (str): The username to filter expenses.
        start_date (str): Start date (YYYY-MM-DD).
        end_date (str): End date (YYYY-MM-DD).

    Returns:
        pd.DataFrame: DataFrame with columns:
            - id (int): Expense record ID.
            - date (datetime64): Expense date.
            - category (str): Expense category.
            - amount (float): Expense amount.
            - description (str): Expense description.
    """
    with sql.connect("data/finance.db") as conn:
        df = pd.read_sql_query(
            """
            SELECT id, date, category, amount, description
            FROM expenses
            WHERE username=?
              AND date BETWEEN ? AND ?
            ORDER BY date ASC
            """,
            conn, params=(username, start_date, end_date)
        )

    if not df.empty:
        df = df.copy()
        df["date"] = pd.to_datetime(df["date"], errors="coerce")
        df["amount"] = pd.to_numeric(df["amount"], errors="coerce")

    return df


def get_user_income_range(username: str,
                          start_date: str,
                          end_date: str) -> pd.DataFrame:
    """
    Retrieve all income for a user within a date range.

    Args:
        username (str): The username to filter income.
        start_date (str): Start date (YYYY-MM-DD).
        end_date (str): End date (YYYY-MM-DD).

    Returns:
        pd.DataFrame: DataFrame with columns:
            - id (int): Income record ID.
            - date (datetime64): Income date.
            - category (str): Income category.
            - amount (float): Income amount.
            - description (str): Income description.
    """
    with sql.connect("data/finance.db") as conn:
        df = pd.read_sql_query(
            """
            SELECT id, date, category, amount, description
            FROM income
            WHERE username=?
              AND date BETWEEN ? AND ?
            ORDER BY date ASC
            """,
            conn, params=(username, start_date, end_date)
        )

    if not df.empty:
        df = df.copy()
        df["date"] = pd.to_datetime(df["date"], errors="coerce")
        df["amount"] = pd.to_numeric(df["amount"], errors="coerce")

    return df


def get_monthly_expenses(username: str,
                         start_date: str,
                         end_date: str) -> pd.DataFrame:
    """
    Retrieve monthly aggregated expenses (YYYY-MM) for a user.

    Args:
        username (str): The username to filter expenses.
        start_date (str): Start date (YYYY-MM-DD).
        end_date (str): End date (YYYY-MM-DD).

    Returns:
        pd.DataFrame: DataFrame with columns:
            - date (datetime64): Month timestamp.
            - amount (float): Total expenses in that month.
    """
    df = get_user_expenses_range(username, start_date, end_date)
    if df.empty:
        return df

    monthly = (
        df.groupby(df["date"].dt.to_period("M"))["amount"]
        .sum()
        .reset_index()
    )
    monthly["date"] = monthly["date"].dt.to_timestamp()
    return monthly
