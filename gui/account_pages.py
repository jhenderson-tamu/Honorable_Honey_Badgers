# PROGRAM: Account Management Pages
# PURPOSE: Provide a graphical user interface (GUI) for managing
#          user account settings such as changing passwords and
#          viewing login history.
# INPUT:
#   - username (str): Username of the logged-in user.
#   - parent_frame (Frame): Tkinter frame where this page will render.
# PROCESS:
#   - Displays account management options.
#   - Provides form for updating user passwords.
#   - Fetches and displays login history records from the database.
#   - Logs account changes as user actions.
# OUTPUT:
#   - Updated password (if successfully changed).
#   - List of login history records displayed in the GUI.
# HONOR CODE: On my honor, as an Aggie, I have neither given nor
#             received unauthorized aid on this academic work.

import ttkbootstrap as ttk
from operations.database import (
    change_user_password,
    get_user_login_history,
    log_user_action
)


class AccountPages:
    """Class to handle account management GUI pages."""

    def __init__(self, username: str, parent_frame):
        """
        Initialize the AccountPages instance.

        Args:
            username (str): Username of the logged-in user.
            parent_frame (Frame): Tkinter frame where account pages will display.
        """
        self.username = username
        self.parent_frame = parent_frame

    # ------------------------------------------------------------------
    # Main Page
    # ------------------------------------------------------------------
    def create_management_page(self):
        """
        Build and display the account management page.

        Features:
            - Change password section.
            - Login history section.
            - Navigation back to main menu.
        """
        # Clear existing widgets in the parent frame
        for widget in self.parent_frame.winfo_children():
            widget.destroy()

        # Title label
        ttk.Label(
            self.parent_frame,
            text=f"Manage Account - {self.username}",
            font=("Helvetica", 14, "bold")
        ).pack(pady=15)

        # Main frame container
        frame = ttk.Frame(self.parent_frame, padding=20)
        frame.pack(fill="both", expand=True)

        # ------------------------------------------------------------------
        # Password Change Section
        # ------------------------------------------------------------------
        ttk.Label(
            frame, text="Change Password", font=("Helvetica", 12, "bold")
        ).pack(anchor="w", pady=(10, 5))

        ttk.Label(frame, text="Old Password:").pack(anchor="w")
        old_pw_entry = ttk.Entry(frame, show="*")
        old_pw_entry.pack(fill="x", pady=5)

        ttk.Label(frame, text="New Password:").pack(anchor="w")
        new_pw_entry = ttk.Entry(frame, show="*")
        new_pw_entry.pack(fill="x", pady=5)

        status_label = ttk.Label(
            frame, text="", foreground="red", font=("Helvetica", 11, "italic")
        )
        status_label.pack(anchor="center", pady=5)

        def change_password():
            """
            Attempt to change the user's password.

            - Validates old password.
            - Updates the password if valid.
            - Displays success/failure message in the UI.
            - Logs successful password changes.
            """
            old_pw = old_pw_entry.get()
            new_pw = new_pw_entry.get()

            success, message = change_user_password(
                self.username, old_pw, new_pw
            )

            if success:
                status_label.config(text=message, foreground="green")
                log_user_action(self.username, "Password Change")
                old_pw_entry.delete(0, "end")
                new_pw_entry.delete(0, "end")
            else:
                status_label.config(text=message, foreground="red")

        ttk.Button(
            frame, text="Update Password", bootstyle="success",
            command=change_password
        ).pack(pady=10)

        # ------------------------------------------------------------------
        # Login History Section
        # ------------------------------------------------------------------
        ttk.Label(
            frame, text="Login History", font=("Helvetica", 12, "bold")
        ).pack(anchor="w", pady=(20, 5))

        history_frame = ttk.Frame(
            frame, relief="ridge", borderwidth=1, padding=10
        )
        history_frame.pack(fill="both", expand=True)

        rows = get_user_login_history(self.username)

        if not rows:
            ttk.Label(history_frame, text="No login history found.").pack(
                anchor="w"
            )
        else:
            for action, ts in rows:
                ttk.Label(
                    history_frame, text=f"{ts} - {action}"
                ).pack(anchor="w")

        # ------------------------------------------------------------------
        # Back Navigation
        # ------------------------------------------------------------------
        def back_to_main():
            """Clear the frame and return to the main menu."""
            for widget in self.parent_frame.winfo_children():
                widget.destroy()

        ttk.Button(
            frame, text="Back to Main Menu", bootstyle="danger",
            command=back_to_main
        ).pack(pady=20)
