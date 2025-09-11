# PROGRAM: Authentication Window
# PURPOSE: Provide a login and registration interface for users before
# granting access to the main application.
# INPUT: Username and password entered by the user.
# PROCESS: Authenticates the user or registers a new one, logs actions,
# and calls the main application callback on successful login.
# OUTPUT: Authenticated session or registration status message.
# HONOR CODE: On my honor, as an Aggie, I have neither given nor
# received unauthorized aid on this academic work.

import ttkbootstrap as ttk
from ttkbootstrap.constants import YES
from operations.database import (
    register_user,
    authenticate_user,
    log_user_action
)


class AuthWindow:
    """Class to handle the authentication (login/register) GUI."""

    def __init__(self, main_app_callback):
        """
        Initialize the authentication window.

        Args:
            main_app_callback (callable): Function to call on successful
                login, passing the authenticated username.
        """
        self.main_app_callback = main_app_callback
        self.login = ttk.Window(themename="solar")
        self.login.title("Login Page")
        self.login.geometry("400x550")

        self.setup_ui()

    def setup_ui(self):
        """Configure and display the authentication user interface."""
        # Attempt to display image at top of window
        image_path = "images/HHB_1.png"
        try:
            img = ttk.PhotoImage(file=image_path)
            img_label = ttk.Label(self.login, image=img)
            img_label.pack(pady=20)
            img_label.image = img  # Keep reference to prevent GC
        except Exception as e:
            print(f"Error loading image: {e}")

        # Frame for login form
        frame = ttk.Frame(self.login, padding=20)
        frame.pack(fill="both", expand=YES)

        # Dynamic label for feedback messages
        self.label_var = ttk.StringVar(value="")
        ttk.Label(
            self.login,
            textvariable=self.label_var,
            font=("Helvetica", 14, "bold"),
            foreground="red"
        ).pack(pady=5)

        # Username label and entry
        ttk.Label(frame, text="Username:", font=("Helvetica", 12)).pack(
            anchor="w", pady=5
        )
        self.username_entry = ttk.Entry(frame, bootstyle="primary")
        self.username_entry.pack(fill="x", pady=5)

        # Password label and entry
        ttk.Label(frame, text="Password:", font=("Helvetica", 12)).pack(
            anchor="w", pady=5
        )
        self.password_entry = ttk.Entry(
            frame, bootstyle="primary", show="*"
        )
        self.password_entry.pack(fill="x", pady=5)

        # Login button
        ttk.Button(
            frame, text="Login", bootstyle="success",
            command=self.login_user
        ).pack(pady=20)

        # Register button
        ttk.Button(
            frame, text="Register", bootstyle="success",
            command=self.register_user
        ).pack(pady=15)

        # Bind Enter key to trigger login
        self.login.bind("<Return>", lambda event: self.login_user())

    def register_user(self):
        """Register a new user and display the result."""
        username = self.username_entry.get()
        password = self.password_entry.get()

        result = register_user(username, password)
        self.label_var.set(result)

        # Clear password field for security
        self.password_entry.delete(0, "end")

    def login_user(self):
        """Authenticate the user and open the main application on success."""
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
        """Close the login window."""
        self.login.destroy()

    def run(self):
        """Run the login window event loop."""
        self.login.mainloop()
