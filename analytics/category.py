import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import ttkbootstrap as ttk
import pandas as pd
from ttkbootstrap.widgets import DateEntry
from operations import reports
from .helpers import build_table_popup
from tkinter import filedialog, messagebox
import os


class CategoryReport:
    def __init__(self, parent, username, back_callback):
        self.parent = parent
        self.username = username
        self.back_callback = back_callback

    def show(self):
        # clear parent frame
        for w in self.parent.winfo_children():
            w.destroy()

        # get all expenses (used for min/max date)
        all_expenses = reports.get_user_expenses_range(
            self.username, "01/01/1900", "12/31/2999"
        )

        frame = ttk.Frame(self.parent)
        frame.pack(fill="both", expand=True, padx=20, pady=20)

        # default date range
        if not all_expenses.empty:
            min_date = all_expenses["date"].min().date()
            max_date = all_expenses["date"].max().date()
        else:
            today = pd.Timestamp.today().date()
            min_date = max_date = today

        # date pickers
        ttk.Label(frame, text="Start Date:").grid(row=0, column=0, padx=5, pady=5)
        start_date = DateEntry(frame, bootstyle="primary", dateformat="%Y-%m-%d")
        start_date.set_date(min_date)
        start_date.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(frame, text="End Date:").grid(row=0, column=2, padx=5, pady=5)
        end_date = DateEntry(frame, bootstyle="primary", dateformat="%Y-%m-%d")
        end_date.set_date(max_date)
        end_date.grid(row=0, column=3, padx=5, pady=5)

        # total spent label
        total_label = ttk.Label(
            frame,
            text="Total Spent: $0.00",
            font=("Helvetica", 12, "bold"),
            cursor="hand2"
        )
        total_label.grid(row=1, column=0, columnspan=4, pady=10)

        # chart container
        chart_frame = ttk.Frame(frame)
        chart_frame.grid(row=2, column=0, columnspan=5, pady=20)

        def refresh_report(event=None):
            start = start_date.entry.get()
            end = end_date.entry.get()
            df = reports.get_user_expenses_range(self.username, start, end)

            total_spent = df["amount"].sum() if not df.empty else 0
            total_label.config(text=f"Total Spent: ${total_spent:,.2f}")
            total_label.df = df

            for w in chart_frame.winfo_children():
                w.destroy()

            if not df.empty:
                grouped = df.groupby("category")["amount"].sum().reset_index()

                fig, ax = plt.subplots(figsize=(6, 4))

                def autopct_format(pct, allvals):
                    absolute = int(round(pct / 100.0 * sum(allvals)))
                    return f"{pct:.1f}%\n(${absolute:,.0f})"

                wedges, _, _ = ax.pie(
                    grouped["amount"],
                    labels=grouped["category"],
                    autopct=lambda pct: autopct_format(pct, grouped["amount"]),
                    startangle=90
                )
                ax.set_title("Expenses by Category")

                # --- add slice click popup
                def on_pick(event):
                    for i, wedge in enumerate(wedges):
                        if event.artist == wedge:
                            category = grouped.iloc[i]["category"]
                            cat_df = df[df["category"] == category]
                            build_table_popup(
                                self.parent,
                                f"Expenses for {category}",
                                cat_df,
                                export_name=f"{category}_expenses"
                            )
                            break

                for wedge in wedges:
                    wedge.set_picker(True)

                fig.canvas.mpl_connect("pick_event", on_pick)

                # embed chart
                canvas = FigureCanvasTkAgg(fig, master=chart_frame)
                canvas.draw()
                canvas.get_tk_widget().pack(fill="both", expand=True)

                # export chart button
                def export_chart():
                    filepath = filedialog.asksaveasfilename(
                        defaultextension=".png",
                        filetypes=[("PNG Image", "*.png")],
                        title="Save Category Report As"
                    )
                    if filepath:
                        try:
                            fig.savefig(filepath, dpi=150)
                            messagebox.showinfo(
                                "Export Successful",
                                f"Chart saved to:\n{os.path.abspath(filepath)}"
                            )
                        except Exception as e:
                            messagebox.showerror("Export Failed", str(e))

                ttk.Button(
                    chart_frame, text="Export Chart as PNG",
                    bootstyle="info", command=export_chart
                ).pack(pady=10)

                ttk.Button(
                    chart_frame, text="Back",
                    bootstyle="secondary", width=20,
                    command=self.back_callback
                ).pack(pady=10)

        # bind events
        start_date.bind("<<DateEntrySelected>>", refresh_report)
        end_date.bind("<<DateEntrySelected>>", refresh_report)
        total_label.bind(
            "<Button-1>",
            lambda e: build_table_popup(
                self.parent,
                "All Expenses",
                getattr(total_label, "df", pd.DataFrame())
            )
        )

        # initial load
        refresh_report()