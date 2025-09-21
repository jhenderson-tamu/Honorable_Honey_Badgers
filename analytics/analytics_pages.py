import ttkbootstrap as ttk
from .category import CategoryReport
from .monthly import MonthlyReport


class ReportPages:
    def __init__(self, username, parent_frame):
        self.username = username
        self.parent_frame = parent_frame

    def create_report_page(self):
        self._show_report_options()

    def _show_report_options(self):
        for w in self.parent_frame.winfo_children():
            w.destroy()

        ttk.Label(
            self.parent_frame, text="Select a Report",
            font=("Helvetica", 12, "bold")
        ).pack(pady=10)

        frame = ttk.Frame(self.parent_frame, padding=20)
        frame.pack(fill="both", expand=True)

        ttk.Button(frame, text="Expenses by Category (Pie)",
                   bootstyle="info", width=30,
                   command=lambda: CategoryReport(
                       self.parent_frame, self.username, self._show_report_options
                   ).show()).pack(pady=5)

        ttk.Button(frame, text="Monthly Expenses (Bar)",
                   bootstyle="info", width=30,
                   command=lambda: MonthlyReport(
                       self.parent_frame, self.username, self._show_report_options
                   ).show()).pack(pady=5)
