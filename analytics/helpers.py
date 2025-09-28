# PROGRAM: Analytics Helpers
# PURPOSE: Provide reusable helpers for analytics pages including:
#          - Reusable table popup for DataFrames
#          - Consistent action buttons
#          - Standard chart export
#          - Safe detail popup trigger
# INPUT:
#   - parent (Frame): Parent tkinter frame where widgets attach.
#   - title (str): Title text for popups.
#   - df (pd.DataFrame): DataFrame of expense/income data.
#   - export_name (str): Default filename prefix for exports.
# PROCESS:
#   - Build and show table popups.
#   - Provide stacked action buttons with consistent style.
#   - Provide a standardized PNG export for charts.
#   - Safely open detail popups only if data is available.
# OUTPUT:
#   - Interactive popups, buttons, and export dialogs.
# HONOR CODE: On my honor, as an Aggie, I have neither given nor
#             received unauthorized aid on this academic work.

import os
import pandas as pd
import ttkbootstrap as ttk
from tkinter import filedialog, messagebox


# ----------------------------------------------------------------------
# Table Popup
# ----------------------------------------------------------------------
def build_table_popup(parent, title, df, export_name="expenses"):
    """
    Create a popup window with a tabular view of a DataFrame.

    Args:
        parent (Frame): Parent tkinter frame.
        title (str): Window title for the popup.
        df (pd.DataFrame): DataFrame with expense/income data.
        export_name (str, optional): Filename prefix when exporting.
            Defaults to "expenses".

    Returns:
        None. Opens a new popup window with table and export options.
    """
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
        tree.column(
            col,
            width=cfg["width"],
            minwidth=cfg["width"],
            anchor=cfg["anchor"],
            stretch=cfg["stretch"],
        )

    if "date" in df.columns:
        df = df.copy()
        df.loc[:, "date"] = pd.to_datetime(df["date"], errors="coerce")

    df_sorted = df.sort_values(by="date", ascending=False)

    def _fmt_date(dt):
        if pd.notnull(dt):
            if isinstance(dt, str):
                return dt
            return dt.strftime("%Y-%m-%d")
        return ""

    def _fmt_amt(val):
        try:
            return f"${float(val):,.2f}"
        except (ValueError, TypeError):
            return "$0.00"

    for _, row in df_sorted.iterrows():
        tree.insert(
            "",
            "end",
            values=(
                _fmt_date(row.get("date")),
                str(row.get("category", "") or ""),
                _fmt_amt(row.get("amount", 0)),
                str(row.get("description", "") or ""),
            ),
        )

    def export_csv():
        filepath = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV Files", "*.csv")],
            title=f"Save {export_name} As",
        )
        if filepath:
            try:
                df_sorted.to_csv(filepath, index=False)
                messagebox.showinfo(
                    "Export Successful",
                    f"Data exported to:\n{os.path.abspath(filepath)}",
                )
            except Exception as e:
                messagebox.showerror("Export Failed", str(e))

    btn_frame = ttk.Frame(popup)
    btn_frame.pack(fill="x", pady=10)

    ttk.Button(
        btn_frame, text="Export to CSV", bootstyle="info", command=export_csv
    ).pack(side="left", padx=10)

    ttk.Button(
        btn_frame, text="Close", bootstyle="danger", command=popup.destroy
    ).pack(side="right", padx=10)


# ----------------------------------------------------------------------
# Action Buttons
# ----------------------------------------------------------------------
def make_action_buttons(
    parent,
    actions,
    width: int = 25,
    pady: int = 5,
    use_grid: bool = False,
    row: int | None = None,
    column: int = 0,
    columnspan: int = 6,
    sticky: str = "ew",
):
    """
    Create a stack of fixed-width ttkbootstrap buttons.

    Args:
        parent (Frame): Parent tkinter frame.
        actions (list[tuple[str, callable, str]]):
            List of (label, callback, bootstyle).
        width (int): Fixed width of buttons. Defaults to 25.
        pady (int): Vertical padding between buttons. Defaults to 5.
        use_grid (bool): If True, place using grid instead of pack.
        row (int | None): Grid row (if None, auto-places at next available row).
        column (int): Grid column (default=0).
        columnspan (int): How many columns to span when using grid.
        sticky (str): Sticky option for grid placement. Defaults to "ew".

    Returns:
        ttk.Frame: Frame containing the buttons.
    """
    btn_frame = ttk.Frame(parent)

    if use_grid:
        # Auto-place if row not provided
        if row is None:
            # find the next available row in grid
            children = parent.grid_slaves()
            max_row = max((child.grid_info().get("row", 0) for child in children), default=-1)
            row = max_row + 1
        btn_frame.grid(row=row, column=column, columnspan=columnspan, pady=pady, sticky=sticky)
    else:
        btn_frame.pack(pady=pady)

    for i, (label, callback, style) in enumerate(actions):
        ttk.Button(
            btn_frame,
            text=label,
            bootstyle=style,
            width=width,
            command=callback,
        ).pack(pady=(0 if i == 0 else pady))

    return btn_frame


# ----------------------------------------------------------------------
# Chart Export
# ----------------------------------------------------------------------
def export_chart(fig, default_name: str, title: str = "Save Chart As"):
    """
    Export a matplotlib figure as a PNG file.

    Args:
        fig (matplotlib.figure.Figure): The figure to export.
        default_name (str): Default filename (without extension).
        title (str): Dialog title for save-as prompt.

    Returns:
        bool: True if export succeeded, False otherwise.
    """
    filepath = filedialog.asksaveasfilename(
        defaultextension=".png",
        filetypes=[("PNG Image", "*.png")],
        title=title,
        initialfile=f"{default_name}.png",
    )
    if filepath:
        try:
            fig.savefig(filepath, dpi=150, bbox_inches="tight", pad_inches=0.2)
            messagebox.showinfo(
                "Export Successful",
                f"Chart saved to:\n{os.path.abspath(filepath)}",
            )
            return True
        except Exception as error:
            messagebox.showerror("Export Failed", str(error))
    return False


# ----------------------------------------------------------------------
# Expense Popup (Safe Wrapper)
# ----------------------------------------------------------------------
def open_expense_popup(parent, title: str, df: pd.DataFrame, export_name: str = "expenses"):
    """
    Safely open a detail popup for expenses/income.

    Args:
        parent (Frame): Parent tkinter frame.
        title (str): Window title for the popup.
        df (pd.DataFrame): Expense/income data.
        export_name (str): Filename prefix when exporting.

    Returns:
        None
    """
    if df is None or df.empty:
        messagebox.showinfo("No Data", "No records available to display.")
        return
    build_table_popup(parent, title, df, export_name=export_name)
