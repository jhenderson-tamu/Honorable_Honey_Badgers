# PROGRAM: Reports Operations
# PURPOSE: Provide data access functions for generating expense reports
# INPUT: Username, optional date ranges
# PROCESS: Query SQLite database and return results as pandas DataFrames
# OUTPUT: DataFrames ready for use in charts/tables
# HONOR CODE: On my honor, as an Aggie, I have neither given nor
# received unauthorized aid on this academic work.

import sqlite3 as sql
import pandas as pd


def get_user_expenses_df(username: str) -> pd.DataFrame:
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
        """, conn, params=(username,))
    return df


def get_user_expenses_df(username: str) -> pd.DataFrame:
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
        """, conn, params=(username,))
    return df

def get_user_expenses_range(username: str, start_date: str, end_date: str) -> pd.DataFrame:
    """
    Return all expenses for a given user within a date range.
    Filtering is done in pandas to handle MM/DD/YYYY text dates.
    """
    with sql.connect("data/finance.db") as conn:
        df = pd.read_sql_query("""
            SELECT id, date, category, amount, description
            FROM expenses
            WHERE username=?
            ORDER BY date ASC
        """, conn, params=(username,))

    if df.empty:
        return df

    # Normalize types
    df["date"] = pd.to_datetime(df["date"], errors="coerce", format="%m/%d/%Y")
    df["amount"] = pd.to_numeric(df["amount"], errors="coerce")

    # Convert inputs to datetime
    start = pd.to_datetime(start_date, errors="coerce")
    end = pd.to_datetime(end_date, errors="coerce")

    # Filter in pandas
    mask = (df["date"] >= start) & (df["date"] <= end)
    df = df.loc[mask]

    return df
