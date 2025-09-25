import os
import pandas as pd
import ttkbootstrap as ttk
from tkinter import filedialog, messagebox


def build_table_popup(parent, title, df, export_name="expenses"):
    """Reusable popup table with CSV export."""
    if df.empty:
        return

    popup = ttk.Toplevel(parent)
    popup.title(title)
    popup.geometry("800x400")

    cols = ("Date", "Category", "Amount", "Description")

    table_frame = ttk.Frame(popup)
    table_frame.pack(fill="both", expand=True, padx=10, pady=10)
    table_frame.columnconfigure(0, weight=1)
    table_frame.rowconfigure(0, weight=1)

    tree = ttk.Treeview(table_frame, columns=cols, show="headings")
    tree.grid(row=0, column=0, sticky="nsew")

    vscroll = ttk.Scrollbar(table_frame, orient="vertical", command=tree.yview)
    hscroll = ttk.Scrollbar(table_frame, orient="horizontal", command=tree.xview)
    tree.configure(yscrollcommand=vscroll.set, xscrollcommand=hscroll.set)
    vscroll.grid(row=0, column=1, sticky="ns")
    hscroll.grid(row=1, column=0, sticky="ew")

    specs = {
        "Date": {"width": 110, "anchor": "center", "stretch": False},
        "Category": {"width": 160, "anchor": "w", "stretch": False},
        "Amount": {"width": 110, "anchor": "e", "stretch": False},
        "Description": {"width": 420, "anchor": "w", "stretch": True},
    }

    for col in cols:
        cfg = specs[col]
        tree.heading(col, text=col, anchor=cfg["anchor"])
        tree.column(col, width=cfg["width"], minwidth=cfg["width"],
                    anchor=cfg["anchor"], stretch=cfg["stretch"])

    # --- Ensure date is datetime before sorting ---
    if "date" in df.columns:
        df = df.copy() #ensure we're working on a fresh Dataframe
        df.loc[:, "date"] = pd.to_datetime(df["date"], errors="coerce")

    df_sorted = df.sort_values(by="date", ascending=False)

    def _fmt_date(dt):
        if pd.notnull(dt):
            if isinstance(dt, str):
                return dt  # assume already YYYY-MM-DD string
            return dt.strftime("%Y-%m-%d")
        return ""

    def _fmt_amt(val):
        try:
            return f"${float(val):,.2f}"
        except (ValueError, TypeError):
            return "$0.00"

    # --- Insert rows into table ---
    for _, row in df_sorted.iterrows():
        tree.insert("", "end", values=(
            _fmt_date(row.get("date")),
            str(row.get("category", "") or ""),
            _fmt_amt(row.get("amount", 0)),
            str(row.get("description", "") or "")
        ))

    # --- CSV Export ---
    def export_csv():
        filepath = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV Files", "*.csv")],
            title=f"Save {export_name} As"
        )
        if filepath:
            try:
                df_sorted.to_csv(filepath, index=False)
                messagebox.showinfo(
                    "Export Successful",
                    f"Expenses exported to:\n{os.path.abspath(filepath)}"
                )
            except Exception as e:
                messagebox.showerror("Export Failed", str(e))

    # --- Buttons ---
    btn_frame = ttk.Frame(popup)
    btn_frame.pack(fill="x", pady=10)
    ttk.Button(btn_frame, text="Export to CSV", bootstyle="info",
               command=export_csv).pack(side="left", padx=10)
    ttk.Button(btn_frame, text="Close", bootstyle="danger",
               command=popup.destroy).pack(side="right", padx=10)
