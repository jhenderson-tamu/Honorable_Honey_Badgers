
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from operations.database import (register_user, authenticate_user,
                                 log_user_action)

class AuthWindow:
    """Authentication window class"""
    
    def __init__(self, main_app_callback):
        self.main_app_callback = main_app_callback
        self.login = ttk.Window(themename="solar")
        self.login.title("Login Page")
        self.login.geometry("400x550")
        
        self.setup_ui()
    
    def setup_ui(self):
        """Set up the authentication UI"""
        # Try to add image at the top
        image_path = "images/HHB_1.png"
        try:
            img = ttk.PhotoImage(file=image_path)
            img_label = ttk.Label(self.login, image=img)
            img_label.pack(pady=20)
            # Keep reference to prevent garbage collection
            img_label.image = img
        except Exception as e:
            print(f"Error loading image: {e}")
        
        # Add a frame for the login form
        frame = ttk.Frame(self.login, padding=20)
        frame.pack(fill="both", expand=YES)
        
        # Dynamic label for messages
        self.label_var = ttk.StringVar()
        self.label_var.set("")
        
        my_label = ttk.Label(self.login, textvariable=self.label_var,
                             font=("Helvetica", 14, "bold"), foreground="red")
        my_label.pack(pady=5)
        
        # Username label and entry
        username_label = ttk.Label(frame, text="Username:", font=("Helvetica", 12))
        username_label.pack(anchor="w", pady=5)
        self.username_entry = ttk.Entry(frame, bootstyle="primary")
        self.username_entry.pack(fill="x", pady=5)
        
        # Password label and entry
        password_label = ttk.Label(frame, text="Password:", font=("Helvetica", 12))
        password_label.pack(anchor="w", pady=5)
        self.password_entry = ttk.Entry(frame, bootstyle="primary", show="*")
        self.password_entry.pack(fill="x", pady=5)
        
        # Login button
        login_button = ttk.Button(frame, text="Login", bootstyle="success",
                                  command=self.login_user)
        login_button.pack(pady=20)
        
        # Register button
        register_button = ttk.Button(frame, text="Register", bootstyle="success",
                                     command=self.register_user)
        register_button.pack(pady=15)
        
        # Bind Enter key to log in
        self.login.bind('<Return>', lambda event: self.login_user())
    
    def register_user(self):
        """Handle user registration"""
        username = self.username_entry.get()
        password = self.password_entry.get()
        
        result = register_user(username, password)
        self.label_var.set(result)
        
        # Clear password field
        self.password_entry.delete(0, "end")
    
    def login_user(self):
        """Handle user login"""
        username = self.username_entry.get()
        password = self.password_entry.get()
        
        success, message = authenticate_user(username, password)
        
        if success:
            log_user_action(username, "Login")
            self.close_login()
            self.main_app_callback(username)
        else:
            self.label_var.set(message)
            self.password_entry.delete(0, "end")
    
    def close_login(self):
        """Close the login window"""
        self.login.destroy()
    
    def run(self):
        """Run the authentication window"""
        self.login.mainloop()