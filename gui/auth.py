# PROGRAM: Authentication Window
# PURPOSE:
#   Provide a login and registration interface for users before granting
#   access to the main application.
# INPUT:
#   - Username and password entered by the user
#   - Registration details for new accounts
# PROCESS:
#   - Authenticates the user or registers a new one
#   - Validates password strength and confirm password match
#   - Displays real-time inline feedback for all password rules
#   - Logs user actions to the database
#   - Calls the main application callback on successful login
# OUTPUT:
#   - Authenticated session or registration status message
# HONOR CODE:
#   On my honor, as an Aggie, I have neither given nor received
#   unauthorized aid on this academic work.

import re
import ttkbootstrap as ttk
from ttkbootstrap.constants import YES
from operations.database import (
    register_user,
    authenticate_user,
    log_user_action,
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

        # State variables
        self.username_entry = None
        self.password_entry = None
        self.confirm_entry = None
        self.password_var = None
        self.confirm_var = None
        self.rules_labels = {}
        self.register_button = None
        self.message_label = None

        self.setup_ui()

    # ------------------------------------------------------------------
    # UI Setup
    # ------------------------------------------------------------------
    def setup_ui(self):
        """Configure and display the login interface."""
        self._clear_window()
        self._set_geometry(400, 600)  # fixed size, centered

        # --- Image banner ---
        image_path = "images/HHB_1.png"
        try:
            img = ttk.PhotoImage(file=image_path)
            img_label = ttk.Label(self.login, image=img)
            img_label.pack(pady=20)
            img_label.image = img
        except Exception as e:
            print(f"Error loading image: {e}")

        # --- Title ---
        ttk.Label(
            self.login, text="Please login",
            font=("Helvetica", 14, "bold")
        ).pack(pady=5)

        # --- Frame for login form ---
        frame = ttk.Frame(self.login, padding=20)
        frame.pack(fill="both", expand=YES)

        # Message label for inline feedback
        self.message_label = ttk.Label(
            self.login, text="", font=("Helvetica", 12),
            foreground="red"
        )
        self.message_label.pack(pady=5)

        # Username
        ttk.Label(frame, text="Username:", font=("Helvetica", 12)).pack(
            anchor="w", pady=5
        )
        self.username_entry = ttk.Entry(frame, bootstyle="primary")
        self.username_entry.pack(fill="x", pady=5)

        # Password
        ttk.Label(frame, text="Password:", font=("Helvetica", 12)).pack(
            anchor="w", pady=5
        )
        self.password_entry = ttk.Entry(
            frame, bootstyle="primary", show="*"
        )
        self.password_entry.pack(fill="x", pady=5)

        # Buttons
        ttk.Button(
            frame, text="Login", bootstyle="success",
            command=self.login_user
        ).pack(pady=20)

        ttk.Button(
            frame, text="Register", bootstyle="info",
            command=self._show_register_page
        ).pack(pady=10)

        # Bind Enter key
        self.login.bind("<Return>", lambda event: self.login_user())

    # ------------------------------------------------------------------
    # Register Page
    # ------------------------------------------------------------------
    def _show_register_page(self):
        """Show the registration form with password rules."""
        self._clear_window()
        self.login.title("Register Page")
        self._set_geometry(400, 770)  # fixed size, centered

        # --- Image banner ---
        image_path = "images/HHB_1.png"
        try:
            img = ttk.PhotoImage(file=image_path)
            img_label = ttk.Label(self.login, image=img)
            img_label.pack(pady=20)
            img_label.image = img
        except Exception as e:
            print(f"Error loading image: {e}")

        ttk.Label(
            self.login, text="Please register",
            font=("Helvetica", 14, "bold")
        ).pack(pady=5)

        frame = ttk.Frame(self.login, padding=20)
        frame.pack(fill="both", expand=YES)

        # Username
        ttk.Label(frame, text="Username:", font=("Helvetica", 12)).pack(
            anchor="w", pady=5
        )
        self.username_entry = ttk.Entry(frame, bootstyle="primary")
        self.username_entry.pack(fill="x", pady=5)

        # Password
        ttk.Label(frame, text="Password:", font=("Helvetica", 12)).pack(
            anchor="w", pady=5
        )
        self.password_var = ttk.StringVar()
        self.password_entry = ttk.Entry(
            frame, bootstyle="primary", show="*",
            textvariable=self.password_var
        )
        self.password_entry.pack(fill="x", pady=5)

        # Confirm password
        ttk.Label(
            frame, text="Confirm Password:", font=("Helvetica", 12)
        ).pack(anchor="w", pady=5)
        self.confirm_var = ttk.StringVar()
        self.confirm_entry = ttk.Entry(
            frame, bootstyle="primary", show="*",
            textvariable=self.confirm_var
        )
        self.confirm_entry.pack(fill="x", pady=5)

        # Password rules section
        ttk.Label(
            frame, text="Password requirements must be met:",
            font=("Helvetica", 10, "italic")
        ).pack(anchor="w", pady=(10, 0))

        rules_frame = ttk.Frame(frame, padding=(20, 5, 0, 5))
        rules_frame.pack(pady=5, anchor="w")

        self.rules_labels = {
            "length": ttk.Label(
                rules_frame, text="At least 8 characters", foreground="red"
            ),
            "uppercase": ttk.Label(
                rules_frame, text="At least 1 uppercase letter", foreground="red"
            ),
            "number": ttk.Label(
                rules_frame, text="At least 1 number", foreground="red"
            ),
            "special": ttk.Label(
                rules_frame, text="At least 1 special character", foreground="red"
            ),
            "no_space": ttk.Label(
                rules_frame, text="No spaces", foreground="red"
            ),
            "match": ttk.Label(
                rules_frame, text="Passwords must match", foreground="red"
            ),
        }
        for lbl in self.rules_labels.values():
            lbl.pack(anchor="w")

        # Register button (disabled until rules are met)
        self.register_button = ttk.Button(
            frame, text="Register", bootstyle="success",
            command=self.register_user, state="disabled"
        )
        self.register_button.pack(pady=20)

        ttk.Button(
            frame, text="Back to Login", bootstyle="danger",
            command=self.setup_ui
        ).pack(pady=10)

        # Track password and confirm changes
        self.password_var.trace_add(
            "write", lambda *args: self._update_password_rules()
        )
        self.confirm_var.trace_add(
            "write", lambda *args: self._update_password_rules()
        )

    # ------------------------------------------------------------------
    # Authentication Actions
    # ------------------------------------------------------------------
    def register_user(self):
        """Register a new user."""
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()
        confirm = self.confirm_entry.get().strip()

        if not username or not password or not confirm:
            self._show_message("All fields are required!", "red")
            return

        if " " in username:
            self._show_message("Username cannot contain spaces!", "red")
            return

        if password != confirm:
            self._show_message("Passwords do not match!", "red")
            return

        result = register_user(username, password)
        self._show_message(result, "green" if "successfully" in result else "red")

        if "successfully" in result:
            self.setup_ui()

    def login_user(self):
        """Authenticate and log in a user."""
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()

        success, message = authenticate_user(username, password)

        if success:
            log_user_action(username, "Login")
            self.close_login()
            self.main_app_callback(username)
        else:
            if "username" in message.lower():
                self._show_message(
                    "User not found. Please register.", "red"
                )
            else:
                self._show_message(message, "red")
            self.password_entry.delete(0, "end")

    # ------------------------------------------------------------------
    # Helper Methods
    # ------------------------------------------------------------------
    def _update_password_rules(self):
        """Update rule labels dynamically as user types."""
        if not self.rules_labels:
            return

        password = self.password_var.get()
        confirm = self.confirm_var.get() if self.confirm_var else ""

        rules_status = {
            "length": len(password) >= 8,
            "uppercase": any(c.isupper() for c in password),
            "number": any(c.isdigit() for c in password),
            "special": bool(re.search(r"[!@#$%^&*(),.?\":{}|<>]", password)),
            "no_space": " " not in password,
            "match": password == confirm and password != "",
        }

        for key, passed in rules_status.items():
            if key in self.rules_labels:
                try:
                    color = "green" if passed else "red"
                    self.rules_labels[key].config(foreground=color)
                except Exception:
                    continue

        if all(rules_status.values()):
            if self.register_button:
                self.register_button.config(state="normal")
        else:
            if self.register_button:
                self.register_button.config(state="disabled")

    def _show_message(self, text, color):
        """Display an inline message to the user."""
        if self.message_label:
            self.message_label.config(text=text, foreground=color)

    def _clear_window(self):
        """Clear the login window and reset state."""
        for w in self.login.winfo_children():
            w.destroy()
        self.rules_labels = {}
        self.register_button = None
        self.message_label = None
        self.password_var = None
        self.confirm_var = None

    def _set_geometry(self, width, height):
        """Set the window geometry and center it on the screen."""
        self.login.update_idletasks()
        screen_w = self.login.winfo_screenwidth()
        screen_h = self.login.winfo_screenheight()
        x = (screen_w // 2) - (width // 2)
        y = (screen_h // 2) - (height // 2)
        self.login.geometry(f"{width}x{height}+{x}+{y}")

    def close_login(self):
        """Close the login window."""
        self.login.destroy()

    def run(self):
        """Run the login window event loop."""
        self.login.mainloop()
