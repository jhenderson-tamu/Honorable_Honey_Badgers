# operations/reports.py

"""
MODULE: Reports
PURPOSE: Generate expense and profit reports (CSV, PNG, PDF)
INPUT: finance.db path, username, start/end dates
OUTPUT: CSVs, charts, and optional in-memory DataFrames
"""

import sqlite3
from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime

# ------------------------------
# Data Loading
# ------------------------------
def load_tables(db_path: Path):
    conn = sqlite3.connect(str(db_path))
    try:
        def read_or_empty(table):
            try:
                df = pd.read_sql_query(f"SELECT * FROM {table}", conn)
            except Exception:
                df = pd.DataFrame(columns=["id","date","category","amount","description","username"])
            if "date" in df.columns:
                df["date"] = pd.to_datetime(df["date"], errors="coerce")
            if "amount" in df.columns:
                df["amount"] = pd.to_numeric(df["amount"], errors="coerce")
            return df
        expenses = read_or_empty("expenses")
        income = read_or_empty("income")
        return expenses, income
    finally:
        conn.close()

def filter_range_user(df, username: str, start: str, end: str):
    if df.empty:
        return df.copy()
    m = pd.Series([True]*len(df))
    if username:
        m &= (df["username"] == username)
    if start:
        m &= (df["date"] >= pd.to_datetime(start))
    if end:
        m &= (df["date"] < pd.to_datetime(end))
    return df.loc[m].copy()

def expenses_by_category(expenses_df: pd.DataFrame, start: str, end: str, top_n: int = 15):
    if expenses_df.empty:
        return pd.DataFrame(columns=["category","total","percent","txn_count"])
    m = (expenses_df["date"] >= pd.to_datetime(start)) & (expenses_df["date"] < pd.to_datetime(end))
    sub = expenses_df.loc[m].copy()
    if sub.empty:
        return pd.DataFrame(columns=["category","total","percent","txn_count"])
    g = (sub.groupby("category", dropna=False)
            .agg(total=("amount","sum"), txn_count=("id","count"))
            .reset_index())
    if (g["total"] < 0).any():
        g["total"] = g["total"].abs()
    total_sum = g["total"].sum()
    g["percent"] = 0.0 if total_sum == 0 else g["total"] / total_sum
    return g.sort_values("total", ascending=False).head(top_n).reset_index(drop=True)

def profit_by_month(expenses_df: pd.DataFrame, income_df: pd.DataFrame,
                    start: str, end: str, freq: str = "ME"):
    # Normalize deprecated frequency alias
    if freq == "M":
        freq = "ME"
    e = expenses_df.copy()
    i = income_df.copy()
    if not e.empty:
        e = e[(e["date"] >= pd.to_datetime(start)) & (e["date"] < pd.to_datetime(end))]
    if not i.empty:
        i = i[(i["date"] >= pd.to_datetime(start)) & (i["date"] < pd.to_datetime(end))]
    if i.empty and e.empty:
        return pd.DataFrame(columns=["period","income","expenses","profit"])
    inc = (i.set_index("date")["amount"].resample(freq).sum()) if not i.empty else pd.Series(dtype=float)
    exp = (e.set_index("date")["amount"].resample(freq).sum()) if not e.empty else pd.Series(dtype=float)
    exp_sign = -1.0 if (not exp.empty and exp.mean() > 0) else 1.0
    income = inc.fillna(0.0)
    expenses = (exp * exp_sign).fillna(0.0)
    profit = (income + expenses).rename("profit")
    return pd.concat(
        [income.rename("income"), expenses.rename("expenses"), profit],
        axis=1
    ).fillna(0.0).reset_index(names="period")

def plot_expenses_bar(df_cat: pd.DataFrame, title: str, out_png: Path, out_pdf: Path):
    if df_cat.empty:
        return
    plt.figure()
    plt.bar(df_cat["category"], df_cat["total"])
    plt.title(title)
    plt.xticks(rotation=45, ha="right")
    plt.tight_layout()
    plt.savefig(out_png, dpi=160)
    plt.savefig(out_pdf)
    plt.close()

def plot_profit_line(df_profit: pd.DataFrame, title: str, out_png: Path, out_pdf: Path):
    if df_profit.empty:
        return
    plt.figure()
    plt.plot(df_profit["period"], df_profit["profit"], marker="o")
    plt.title(title)
    plt.axhline(0)
    plt.xticks(rotation=45, ha="right")
    plt.tight_layout()
    plt.savefig(out_png, dpi=160)
    plt.savefig(out_pdf)
    plt.close()

def generate_reports(db_path, username, start, end, out_dir="hhb_reports_out"):
    """High-level function for generating reports programmatically."""
    out_path = Path(out_dir)
    out_path.mkdir(exist_ok=True, parents=True)

    expenses_all, income_all = load_tables(db_path)
    expenses_f = filter_range_user(expenses_all, username, start, end)
    income_f = filter_range_user(income_all, username, start, end)

    exp_cat = expenses_by_category(expenses_f, start, end, top_n=15)
    profit_m = profit_by_month(expenses_f, income_f, start, end, freq="M")

    exp_csv = out_path / "expenses_by_category.csv"
    profit_csv = out_path / "profit_by_month.csv"
    exp_cat.to_csv(exp_csv, index=False)
    profit_m.to_csv(profit_csv, index=False)

    plot_expenses_bar(exp_cat, f"Top Categories ({start} to {end}) — user: {username}",
                      out_path / "expenses_by_category.png", out_path / "expenses_by_category.pdf")
    plot_profit_line(profit_m, f"Profit by Month — user: {username}",
                     out_path / "profit_by_month.png", out_path / "profit_by_month.pdf")

    return {
        "expenses_df": exp_cat,
        "profit_df": profit_m,
        "output_dir": out_path
    }