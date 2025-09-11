
import ttkbootstrap as ttk
from operations.database import (change_user_password,
                                   get_user_login_history,
                       log_user_action)

class AccountPages:
    """Class to handle account management GUI pages"""
    
    def __init__(self, username, parent_frame):
        self.username = username
        self.parent_frame = parent_frame
    
    def create_management_page(self):
        """Create the account management page"""
        # Clear any existing widgets
        for widget in self.parent_frame.winfo_children():
            widget.destroy()
        
        # Title label
        ttk.Label(self.parent_frame, text=f"Manage Account - {self.username}",
                  font=("Helvetica", 14, "bold")).pack(pady=15)
        
        frame = ttk.Frame(self.parent_frame, padding=20)
        frame.pack(fill="both", expand=True)
        
        # Password Change Section
        ttk.Label(frame, text="Change Password", 
                  font=("Helvetica", 12, "bold")).pack(anchor="w", pady=(10, 5))
        
        ttk.Label(frame, text="Old Password:").pack(anchor="w")
        old_pw_entry = ttk.Entry(frame, show="*")
        old_pw_entry.pack(fill="x", pady=5)
        
        ttk.Label(frame, text="New Password:").pack(anchor="w")
        new_pw_entry = ttk.Entry(frame, show="*")
        new_pw_entry.pack(fill="x", pady=5)
        
        status_label = ttk.Label(frame, text="", foreground="red",
                                 font=("Helvetica", 11, "italic"))
        status_label.pack(anchor="center", pady=5)
        
        def change_password():
            old_pw = old_pw_entry.get()
            new_pw = new_pw_entry.get()
            
            success, message = change_user_password(self.username, old_pw, new_pw)
            
            if success:
                status_label.config(text=message, foreground="green")
                log_user_action(self.username, "Password Change")
                old_pw_entry.delete(0, "end")
                new_pw_entry.delete(0, "end")
            else:
                status_label.config(text=message, foreground="red")
        
        update_pw_btn = ttk.Button(frame, text="Update Password",
                                   bootstyle="success", command=change_password)
        update_pw_btn.pack(pady=10)
        
        # Login History Section
        ttk.Label(frame, text="Login History", 
                  font=("Helvetica", 12, "bold")).pack(anchor="w", pady=(20, 5))
        
        history_frame = ttk.Frame(frame, relief="ridge", borderwidth=1, padding=10)
        history_frame.pack(fill="both", expand=True)
        
        rows = get_user_login_history(self.username)
        
        if not rows:
            ttk.Label(history_frame, text="No login history found.").pack(anchor="w")
        else:
            for action, ts in rows:
                ttk.Label(history_frame, text=f"{ts} - {action}").pack(anchor="w")
        
        def back_to_main():
            for widget in self.parent_frame.winfo_children():
                widget.destroy()
        
        back_button = ttk.Button(frame, text="Back to Main Menu",
                                 bootstyle="danger", command=back_to_main)
        back_button.pack(pady=20)