# PROGRAM: Category Report
# PURPOSE: Visualize expenses grouped by category for a user within a
#          specified date range using a pie chart.
# INPUT:
#   - username (str): Logged-in user.
#   - parent (Frame): Parent Tkinter frame for rendering content.
#   - back_callback (function): Callback to return to previous page.
# PROCESS:
#   - Retrieve expenses by date range.
#   - Group by category, build pie chart.
#   - On slice left-click, show popup of details.
#   - Allow export of chart.
# OUTPUT: Tkinter-embedded pie chart and table popups.
# HONOR CODE: On my honor, as an Aggie, I have neither given nor
#             received unauthorized aid on this academic work.

import os
import pandas as pd
import matplotlib.pyplot as plt
from tkinter import filedialog, messagebox
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import ttkbootstrap as ttk
from ttkbootstrap.widgets import DateEntry
from operations import reports
from analytics.helpers import build_table_popup, make_action_buttons


class CategoryReport:
    """Page to display expenses grouped by category (pie chart)."""

    def __init__(self, parent, username, back_callback):
        """
        Initialize CategoryReport.

        Args:
            parent (Frame): Tkinter parent frame.
            username (str): Logged-in user.
            back_callback (function): Callback for navigation.
        """
        self.parent = parent
        self.username = username
        self.back_callback = back_callback

    def show(self):
        """Render the Category Report page."""
        for widget in self.parent.winfo_children():
            widget.destroy()

        frame = ttk.Frame(self.parent)
        frame.pack(fill="both", expand=True, padx=20, pady=20)

        # ----------------------------------------------------------
        # Determine default min/max date
        # ----------------------------------------------------------
        all_expenses = reports.get_user_expenses_range(
            self.username, "1900-01-01", "2999-12-31"
        )

        if not all_expenses.empty:
            last_date = all_expenses["date"].max().date()
            first_day = last_date.replace(day=1)
            next_month = (last_date.replace(day=28) + pd.Timedelta(days=4)).replace(day=1)
            last_day = next_month - pd.Timedelta(days=1)
        else:
            today = pd.Timestamp.today().date()
            first_day = today.replace(day=1)
            next_month = (today.replace(day=28) + pd.Timedelta(days=4)).replace(day=1)
            last_day = next_month - pd.Timedelta(days=1)

        # ----------------------------------------------------------
        # Date pickers
        # ----------------------------------------------------------
        ttk.Label(frame, text="Start Date:").grid(row=0, column=0, padx=5, pady=5)
        start_date = DateEntry(frame, bootstyle="primary", dateformat="%Y-%m-%d")
        start_date.set_date(first_day)
        start_date.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(frame, text="End Date:").grid(row=0, column=2, padx=5, pady=5)
        end_date = DateEntry(frame, bootstyle="primary", dateformat="%Y-%m-%d")
        end_date.set_date(last_day)
        end_date.grid(row=0, column=3, padx=5, pady=5)

        total_label = ttk.Label(
            frame,
            text="Total Spent: $0.00",
            font=("Helvetica", 12, "bold"),
            cursor="hand2",
        )
        total_label.grid(row=1, column=0, columnspan=4, pady=10)

        chart_frame = ttk.Frame(frame)
        chart_frame.grid(row=2, column=0, columnspan=5, pady=20, sticky="nsew")
        frame.grid_rowconfigure(2, weight=1)
        frame.grid_columnconfigure(0, weight=1)

        # ----------------------------------------------------------
        # Refresh function
        # ----------------------------------------------------------
        def refresh_report(event=None):
            for widget in chart_frame.winfo_children():
                widget.destroy()

            df = reports.get_user_expenses_range(
                self.username, start_date.entry.get(), end_date.entry.get()
            )

            total_spent = df["amount"].sum() if not df.empty else 0
            total_label.config(text=f"Total Spent: ${total_spent:,.2f}")
            total_label.df = df

            if df.empty:
                return

            grouped = (
                df.groupby("category")["amount"]
                .sum()
                .reset_index()
                .sort_values("amount", ascending=False)
            )

            fig, ax = plt.subplots(figsize=(7, 5))
            colors = plt.cm.tab20(range(len(grouped)))

            wedges, _, autotexts = ax.pie(
                grouped["amount"],
                startangle=90,
                colors=colors,
                autopct="%1.1f%%",
                pctdistance=0.8,
            )

            for autotext in autotexts:
                autotext.set_color("white")
                autotext.set_fontsize(9)
                autotext.set_fontweight("bold")

            total_amount = grouped["amount"].sum()
            labels = [
                f"{cat}: ${amt:,.2f} ({amt / total_amount * 100:.1f}%)"
                for cat, amt in zip(grouped["category"], grouped["amount"])
            ]

            ncol = 2 if len(grouped) <= 10 else 3
            ax.legend(
                wedges,
                labels,
                title="Categories",
                loc="upper center",
                bbox_to_anchor=(0.5, -0.15),
                ncol=ncol,
                fontsize=8,
            )

            # Make space at bottom for legend
            fig.subplots_adjust(bottom=0.3 if ncol == 2 else 0.35)

            ax.set_title("Expenses by Category", fontsize=12, fontweight="bold", pad=20)

            # Slice click (left-click only) -> details popup
            def on_pick(event_pick):
                if (getattr(event_pick, "mouseevent", None) is None or
                        event_pick.mouseevent.button != 1):
                    return
                for i, wedge in enumerate(wedges):
                    if event_pick.artist == wedge:
                        category_val = grouped.iloc[i]["category"]
                        build_table_popup(
                            self.parent,
                            f"Expenses for {category_val}",
                            df[df["category"] == category_val],
                            export_name=f"{category_val}_expenses",
                        )
                        break

            for wedge in wedges:
                wedge.set_picker(True)
            fig.canvas.mpl_connect("pick_event", on_pick)

            canvas = FigureCanvasTkAgg(fig, master=chart_frame)
            canvas.draw()
            canvas.get_tk_widget().pack(fill="both", expand=True)

            def export_chart():
                filepath = filedialog.asksaveasfilename(
                    defaultextension=".png",
                    filetypes=[("PNG Image", "*.png")],
                    title="Save Category Report As",
                )
                if not filepath:
                    return
                fig.savefig(filepath, dpi=150, bbox_inches="tight", pad_inches=0.2)
                messagebox.showinfo(
                    "Export Successful",
                    f"Chart saved to:\n{os.path.abspath(filepath)}",
                )

            make_action_buttons(
                frame,
                [
                    ("Export Chart as PNG", export_chart, "info"),
                    ("Back", self.back_callback, "danger"),
                ],
                width=25,
                use_grid=True,
            )

        start_date.bind("<<DateEntrySelected>>", refresh_report)
        end_date.bind("<<DateEntrySelected>>", refresh_report)
        total_label.bind(
            "<Button-1>",
            lambda e: build_table_popup(
                self.parent,
                "All Expenses",
                getattr(total_label, "df", pd.DataFrame()),
            ),
        )

        refresh_report()
