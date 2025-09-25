# PROGRAM: Reports Operations
# PURPOSE: Provide data access functions for generating expense reports
# INPUT: Username, optional date ranges
# PROCESS: Query SQLite database and return results as pandas DataFrames
# OUTPUT: DataFrames ready for use in charts/tables
# HONOR CODE: On my honor, as an Aggie, I have neither given nor
# received unauthorized aid on this academic work.

import sqlite3 as sql
import pandas as pd


def get_user_expenses_by_category(username: str) -> pd.DataFrame:
    """
    Return expenses grouped by category for a given user.
    Used for the Expenses by Category (Pie) chart.
    """
    with sql.connect("data/finance.db") as conn:
        df = pd.read_sql_query("""
            SELECT category, SUM(amount) AS total
            FROM expenses
            WHERE username=?
            GROUP BY category
            ORDER BY total DESC
        """, conn, params=(username,))
    return df


def get_user_expenses_range(username: str, start_date: str, end_date: str) -> pd.DataFrame:
    """
    Return all expenses for a given user within a date range.
    Dates are stored in ISO format (YYYY-MM-DD), so SQL filtering works directly.
    """
    with sql.connect("data/finance.db") as conn:
        df = pd.read_sql_query("""
            SELECT id, date, category, amount, description
            FROM expenses
            WHERE username=?
              AND date BETWEEN ? AND ?
            ORDER BY date ASC
        """, conn, params=(username, start_date, end_date))

    if not df.empty:
        df = df.copy()  # prevent SettingWithCopyWarning
        df["date"] = pd.to_datetime(df["date"], errors="coerce")
        df["amount"] = pd.to_numeric(df["amount"], errors="coerce")

    return df


def get_user_income_range(username: str, start_date: str, end_date: str) -> pd.DataFrame:
    """
    Return all income for a given user within a date range.
    """
    with sql.connect("data/finance.db") as conn:
        df = pd.read_sql_query("""
            SELECT id, date, category, amount, description
            FROM income
            WHERE username=?
              AND date BETWEEN ? AND ?
            ORDER BY date ASC
        """, conn, params=(username, start_date, end_date))

    if not df.empty:
        df = df.copy()  # prevent SettingWithCopyWarning
        df["date"] = pd.to_datetime(df["date"], errors="coerce")
        df["amount"] = pd.to_numeric(df["amount"], errors="coerce")

    return df


def get_monthly_expenses(username: str, start_date: str, end_date: str) -> pd.DataFrame:
    """
    Return monthly aggregated expenses (YYYY-MM) for a user.
    """
    df = get_user_expenses_range(username, start_date, end_date)
    if df.empty:
        return df
    monthly = df.groupby(df["date"].dt.to_period("M"))["amount"].sum().reset_index()
    monthly["date"] = monthly["date"].dt.to_timestamp()
    return monthly
