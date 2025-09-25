# PROGRAM: Authentication Window
# PURPOSE:
#   Provide user authentication functionality for login and registration.
# INPUT:
#   - Username and password entered by the user
#   - Confirm password when registering a new account
# PROCESS:
#   - Displays login and registration forms
#   - Validates password against complexity rules:
#       * At least 8 characters
#       * At least 1 uppercase letter
#       * At least 1 number
#       * At least 1 special character
#       * No spaces allowed
#   - Provides inline visual feedback for rules (red → unmet, green → met)
#   - Handles user login and registration, with bcrypt password hashing
#   - Keeps both login and registration windows at a fixed size (400x600)
#   - Automatically centers the window on the user’s screen
# OUTPUT:
#   - If login successful → opens the main application
#   - If registration successful → prompts user to login
# HONOR CODE:
#   On my honor, as an Aggie, I have neither given nor received
#   unauthorized aid on this academic work.

import re
import ttkbootstrap as ttk
from ttkbootstrap.constants import YES
from tkinter import StringVar
from operations.database import (
    authenticate_user,
    register_user,
    log_user_action,
)


class AuthWindow:
    """Authentication window for login and registration."""

    def __init__(self, on_success_callback):
        """
        Initialize the authentication window.

        Args:
            on_success_callback (callable): Function to call after
            successful login.
        """
        self.on_success_callback = on_success_callback
        self.login = ttk.Window(themename="solar")
        self.login.title("Authentication")

        # Variables
        self.username_var = StringVar()
        self.password_var = StringVar()
        self.confirm_var = StringVar()

        self.message_label = None
        self.rules_labels = {}
        self.register_button = None

        # Password rules
        self.password_rules = {
            "length": "At least 8 characters",
            "uppercase": "At least 1 uppercase letter",
            "number": "At least 1 number",
            "special": "At least 1 special character",
            "no_space": "No spaces allowed",
        }

    # ------------------------------------------------------------------
    # UI Setup
    # ------------------------------------------------------------------
    def setup_ui(self):
        """Configure and display the login interface."""
        self._clear_window()
        self._set_geometry(400, 600)  # Fixed + centered

        # Banner image
        image_path = "images/HHB_1.png"
        try:
            img = ttk.PhotoImage(file=image_path)
            img_label = ttk.Label(self.login, image=img)
            img_label.pack(pady=10)
            img_label.image = img
        except Exception as e:
            print(f"Error loading image: {e}")

        ttk.Label(
            self.login,
            text="Please Login",
            font=("Helvetica", 14, "bold")
        ).pack(pady=10)

        # Feedback message
        self.message_label = ttk.Label(
            self.login,
            text="",
            font=("Helvetica", 12, "bold"),
            foreground="red"
        )
        self.message_label.pack(pady=5)

        # Frame for form
        frame = ttk.Frame(self.login, padding=10)
        frame.pack(fill="both", expand=YES)

        ttk.Label(frame, text="Username:").pack(anchor="w", pady=5)
        ttk.Entry(
            frame, textvariable=self.username_var,
            bootstyle="primary"
        ).pack(fill="x", pady=5)

        ttk.Label(frame, text="Password:").pack(anchor="w", pady=5)
        ttk.Entry(
            frame, textvariable=self.password_var,
            bootstyle="primary", show="*"
        ).pack(fill="x", pady=5)

        ttk.Button(
            frame, text="Login", bootstyle="success",
            command=self.login_user
        ).pack(pady=10)

        ttk.Button(
            frame, text="Register", bootstyle="secondary",
            command=self._show_register_page
        ).pack(pady=5)

    # ------------------------------------------------------------------
    # Register Page
    # ------------------------------------------------------------------
    def _show_register_page(self):
        """Display the registration form."""
        self._clear_window()
        self._set_geometry(400, 700)  # Fixed + centered

        # Banner image
        image_path = "images/HHB_1.png"
        try:
            img = ttk.PhotoImage(file=image_path)
            img_label = ttk.Label(self.login, image=img)
            img_label.pack(pady=10)
            img_label.image = img
        except Exception as e:
            print(f"Error loading image: {e}")

        ttk.Label(
            self.login,
            text="Please Register",
            font=("Helvetica", 14, "bold")
        ).pack(pady=10)

        self.message_label = ttk.Label(
            self.login,
            text="",
            font=("Helvetica", 12, "bold"),
            foreground="red"
        )
        self.message_label.pack(pady=5)

        frame = ttk.Frame(self.login, padding=10)
        frame.pack(fill="both", expand=YES)

        # Username
        ttk.Label(frame, text="Username:").pack(anchor="w", pady=5)
        ttk.Entry(
            frame, textvariable=self.username_var,
            bootstyle="primary"
        ).pack(fill="x", pady=5)

        # Password
        ttk.Label(frame, text="Password:").pack(anchor="w", pady=5)
        ttk.Entry(
            frame, textvariable=self.password_var,
            bootstyle="primary", show="*"
        ).pack(fill="x", pady=5)

        # Confirm Password
        ttk.Label(frame, text="Confirm Password:").pack(anchor="w", pady=5)
        ttk.Entry(
            frame, textvariable=self.confirm_var,
            bootstyle="primary", show="*"
        ).pack(fill="x", pady=5)

        # Rules
        rules_frame = ttk.Frame(frame)
        rules_frame.pack(pady=10, fill="x")

        self.rules_labels = {}
        for key, rule in self.password_rules.items():
            lbl = ttk.Label(
                rules_frame, text=rule,
                font=("Helvetica", 10), foreground="red"
            )
            lbl.pack(anchor="w")
            self.rules_labels[key] = lbl

        # Register button (disabled until valid)
        self.register_button = ttk.Button(
            frame, text="Register", bootstyle="success",
            command=self.register_user, state="disabled"
        )
        self.register_button.pack(pady=10)

        ttk.Button(
            frame, text="Back to Login", bootstyle="secondary",
            command=self.setup_ui
        ).pack(pady=5)

        # Monitor password entry live
        self.password_var.trace_add(
            "write", lambda *args: self._update_password_rules()
        )

    # ------------------------------------------------------------------
    # Validation
    # ------------------------------------------------------------------
    def _update_password_rules(self):
        """Live update password rule indicators."""
        password = self.password_var.get()
        rules = {
            "length": len(password) >= 8,
            "uppercase": any(c.isupper() for c in password),
            "number": any(c.isdigit() for c in password),
            "special": bool(re.search(r"[!@#$%^&*(),.?\":{}|<>]", password)),
            "no_space": " " not in password,
        }

        all_passed = True
        for key, passed in rules.items():
            color = "green" if passed else "red"
            if key in self.rules_labels:
                self.rules_labels[key].config(foreground=color)
            if not passed:
                all_passed = False

        if self.register_button:
            self.register_button.config(
                state="normal" if all_passed else "disabled"
            )

    # ------------------------------------------------------------------
    # Authentication Logic
    # ------------------------------------------------------------------
    def login_user(self):
        """Authenticate the user."""
        username = self.username_var.get().strip()
        password = self.password_var.get().strip()

        if not username or not password:
            self.message_label.config(
                text="Please enter both username and password."
            )
            return

        success, message = authenticate_user(username, password)
        if success:
            log_user_action(username, "Login")
            self.login.destroy()
            self.on_success_callback(username)
        else:
            if "Invalid username" in message:
                self.message_label.config(
                    text="User not found. Please register."
                )
            else:
                self.message_label.config(text=message)

    def register_user(self):
        """Register a new user."""
        username = self.username_var.get().strip()
        password = self.password_var.get().strip()
        confirm = self.confirm_var.get().strip()

        if not username or not password or not confirm:
            self.message_label.config(text="All fields are required!")
            return

        if password != confirm:
            self.message_label.config(text="Passwords do not match!")
            return

        result = register_user(username, password)
        if "successfully" in result:
            log_user_action(username, "Register")
            self.message_label.config(
                text="Registration successful! Please login.",
                foreground="green"
            )
        else:
            self.message_label.config(text=result, foreground="red")

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------
    def _clear_window(self):
        """Remove all widgets from the window safely."""
        for widget in self.login.winfo_children():
            widget.destroy()
        self.message_label = None
        self.rules_labels = {}
        self.register_button = None

    def _set_geometry(self, width: int, height: int):
        """Center the window on screen with fixed size."""
        screen_w = self.login.winfo_screenwidth()
        screen_h = self.login.winfo_screenheight()
        x = int((screen_w / 2) - (width / 2))
        y = int((screen_h / 2) - (height / 2))
        self.login.geometry(f"{width}x{height}+{x}+{y}")

    # ------------------------------------------------------------------
    # Main Loop
    # ------------------------------------------------------------------
    def run(self):
        """Run the authentication window loop."""
        self.setup_ui()
        self.login.mainloop()
