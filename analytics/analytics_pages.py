import ttkbootstrap as ttk
from .category import CategoryReport
from .monthly import MonthlyReport


class AnalyticPages:
    def __init__(self, username, parent_frame):
        self.username = username
        self.parent_frame = parent_frame

    def create_analytic_page(self):
        self._show_analytic_options()

    def _show_analytic_options(self):
        # Clear any existing widgets
        for w in self.parent_frame.winfo_children():
            w.destroy()

        ttk.Label(
            self.parent_frame, text="Select an Analytic Option",
            font=("Helvetica", 12, "bold")
        ).pack(pady=10)

        frame = ttk.Frame(self.parent_frame, padding=20)
        frame.pack(fill="both", expand=True)

        ttk.Button(
            frame, text="Expenses by Category Report (Pie)",
            bootstyle="info", width=30,
            command=lambda: CategoryReport(
                self.parent_frame, self.username, self._show_report_options
            ).show()
        ).pack(pady=5)

        ttk.Button(
            frame, text="Monthly Expenses Report (Bar)",
            bootstyle="info", width=30,
            command=lambda: MonthlyReport(
                self.parent_frame, self.username, self._show_report_options
            ).show()
        ).pack(pady=5)

        # --- New Close Button ---
        def close_analytics_page():
            """Clear the parent frame to close the analytics page."""
            for w in self.parent_frame.winfo_children():
                w.destroy()

        ttk.Button(
            frame, text="Close Analytics Page",
            bootstyle="danger", width=30,
            command=close_analytics_page
        ).pack(pady=10)
