
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from operations.database import log_user_action
from gui.expense_pages import ExpensePages
from gui.income_pages import IncomePages
from gui.budget_pages import BudgetPages
from gui.account_pages import AccountPages

class MainApp:
    """Main application window class"""
    
    def __init__(self, username):
        self.username = username
        self.setup_main_window()
    
    def setup_main_window(self):
        """Set up the main application window"""
        # Empty style instance before creating main app
        ttk.Style.instance = None
        
        # Create the main page window after a successful login
        self.main = ttk.Window(themename="solar")
        self.main.title("Main Application")
        self.main.geometry("800x800")
        
        # Welcome message at the top
        welcome_label = ttk.Label(self.main, text=f"Welcome, {self.username}!",
                                  font=("Helvetica", 16, "bold"))
        welcome_label.pack(pady=10)
        
        # Main container to hold sidebar and content frame
        container = ttk.Frame(self.main)
        container.pack(fill="both", expand=YES)
        
        # Sidebar frame on the left for buttons
        self.sidebar = ttk.Frame(container, padding=10)
        self.sidebar.pack(side="left", fill="y")
        
        # Content frame on the right for displaying menus/pages
        self.content_frame = ttk.Frame(container, padding=10, relief="ridge",
                                       borderwidth=2)
        self.content_frame.pack(side="right", fill="both", expand=YES)
        
        # Initialize page classes
        self.expense_pages = ExpensePages(self.username, self.content_frame)
        self.income_pages = IncomePages(self.username, self.content_frame)
        self.budget_pages = BudgetPages(self.username, self.content_frame)
        self.account_pages = AccountPages(self.username, self.content_frame)
        
        self.setup_sidebar()
    
    def setup_sidebar(self):
        """Set up the sidebar with navigation buttons"""
        ttk.Button(self.sidebar, text="Expenses", bootstyle="primary",
                   command=self.show_expenses).pack(fill="x", pady=5)
        ttk.Button(self.sidebar, text="Income", bootstyle="primary",
                   command=self.show_income).pack(fill="x", pady=5)
        ttk.Button(self.sidebar, text="Budget", bootstyle="primary",
                   command=self.show_budget).pack(fill="x", pady=5)
        ttk.Button(self.sidebar, text="Reports", bootstyle="primary",
                   command=self.show_reports).pack(fill="x", pady=5)
        ttk.Button(self.sidebar, text="Manage Account", bootstyle="primary",
                   command=self.show_account).pack(fill="x", pady=5)
        ttk.Button(self.sidebar, text="Logout", bootstyle="danger",
                   command=self.logout).pack(fill="x", pady=20)
    
    def clear_content_frame(self):
        """Clear all widgets from the content frame"""
        for widget in self.content_frame.winfo_children():
            widget.destroy()
    
    def show_expenses(self):
        """Show expenses page"""
        self.clear_content_frame()
        self.expense_pages.create_expenses_page()
    
    def show_income(self):
        """Show income page"""
        self.clear_content_frame()
        self.income_pages.create_income_page()
    
    def show_budget(self):
        """Show budget page"""
        self.clear_content_frame()
        self.budget_pages.create_budget_page()
    
    def show_reports(self):
        """Show reports page (placeholder)"""
        self.clear_content_frame()
        label = ttk.Label(self.content_frame, text="Reports Page - Coming Soon!",
                          font=("Helvetica", 14))
        label.pack(pady=20)
    
    def show_account(self):
        """Show account management page"""
        self.clear_content_frame()
        self.account_pages.create_management_page()
    
    def logout(self):
        """Handle user logout"""
        log_user_action(self.username, "Logout")
        self.main.destroy()
    
    def run(self):
        """Run the main application"""
        self.main.mainloop()