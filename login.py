import customtkinter as ctk
from theme import *  # noqa: F401,F403
from tkinter import messagebox
import re
import json
import os
import hashlib
import subprocess
import sys


# =========================================================
# SMART ATTENDANCE - LOGIN & SIGN UP
# =========================================================



# =========================================================
# COLORS
# =========================================================



# =========================================================
# FILE PATHS
# =========================================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

USER_FILE = os.path.join(
    BASE_DIR,
    "users.json"
)

MAIN_FILE = os.path.join(
    BASE_DIR,
    "main.py"
)


# =========================================================
# CREATE USER FILE
# =========================================================

if not os.path.exists(USER_FILE):
    with open(USER_FILE, "w", encoding="utf-8") as file:
        json.dump([], file, indent=4)


# =========================================================
# USER FUNCTIONS
# =========================================================

def load_users():
    try:
        with open(USER_FILE, "r", encoding="utf-8") as file:
            data = json.load(file)

        if isinstance(data, list):
            return data

        return []

    except (FileNotFoundError, json.JSONDecodeError, OSError):
        return []


def save_users(users):
    with open(USER_FILE, "w", encoding="utf-8") as file:
        json.dump(
            users,
            file,
            indent=4,
            ensure_ascii=False
        )


def hash_password(password):
    return hashlib.sha256(
        password.encode("utf-8")
    ).hexdigest()


# =========================================================
# VALIDATION
# =========================================================

def valid_email(email):

    pattern = r"^[^\s@]+@[^\s@]+\.[^\s@]{2,}$"

    return re.match(
        pattern,
        email
    ) is not None


def valid_password(password):

    pattern = (
        r"^(?=.*[A-Za-z])"
        r"(?=.*\d)"
        r"(?=.*[^A-Za-z\d])"
        r".{8,}$"
    )

    return re.match(
        pattern,
        password
    ) is not None


def valid_name(name):

    return re.match(
        r"^[A-Za-z ]{2,60}$",
        name
    ) is not None


def valid_user_id(user_id):

    return re.match(
        r"^[A-Za-z0-9_-]{3,20}$",
        user_id
    ) is not None


# =========================================================
# MAIN APPLICATION
# =========================================================

class SmartAttendanceLogin(ctk.CTk):

    def __init__(self):

        super().__init__()

        self.title(
            "Smart Attendance - Login"
        )

        self.geometry(
            "950x620"
        )

        self.minsize(
            800,
            550
        )
        maximize(self)

        self.configure(
            fg_color=BACKGROUND
        )

        fade_in(self)

        self.create_ui()

        self.show_login()


    # =====================================================
    # MAIN UI
    # =====================================================

    def create_ui(self):

        self.main_frame = ctk.CTkFrame(
            self,
            fg_color=WHITE,
            corner_radius=22
        )

        self.main_frame.pack(
            fill="both",
            expand=True,
            padx=35,
            pady=30
        )

        self.main_frame.grid_columnconfigure(
            0,
            weight=40
        )

        self.main_frame.grid_columnconfigure(
            1,
            weight=60
        )

        self.main_frame.grid_rowconfigure(
            0,
            weight=1
        )


        # =================================================
        # LEFT SIDE
        # =================================================

        self.left_frame = ctk.CTkFrame(
            self.main_frame,
            fg_color=PRIMARY_DARK,
            corner_radius=0
        )

        self.left_frame.grid(
            row=0,
            column=0,
            sticky="nsew"
        )


        # Logo

        self.logo = ctk.CTkLabel(
            self.left_frame,
            text="SA",
            width=60,
            height=60,
            corner_radius=15,
            fg_color=GOLD,
            text_color=INK,
            font=ctk.CTkFont(
                family=FONT_HEAD,
                size=22,
                weight="bold"
            )
        )

        self.logo.pack(
            pady=(80, 25)
        )


        # Title

        self.left_title = ctk.CTkLabel(
            self.left_frame,
            text="Smart Attendance",
            text_color=WHITE,
            font=ctk.CTkFont(
                family=FONT_HEAD,
                size=28,
                weight="bold"
            )
        )

        self.left_title.pack(
            pady=(0, 15)
        )


        # Description

        self.left_description = ctk.CTkLabel(
            self.left_frame,
            text=(
                "Manage student attendance easily,\n"
                "securely and accurately with our\n"
                "smart attendance management system."
            ),
            text_color="#F8F5EF",
            justify="left",
            font=ctk.CTkFont(
                family=FONT_BODY,
                size=13
            )
        )

        self.left_description.pack(
            padx=35
        )


        # Features

        self.features_frame = ctk.CTkFrame(
            self.left_frame,
            fg_color="transparent"
        )

        self.features_frame.pack(
            pady=30,
            padx=35,
            fill="x"
        )


        features = [
            "✓  Easy Attendance Management",
            "✓  Secure Authentication",
            "✓  Student & Faculty Records",
            "✓  Fast and Accurate Attendance"
        ]


        for feature in features:

            label = ctk.CTkLabel(
                self.features_frame,
                text=feature,
                text_color=WHITE,
                anchor="w",
                font=ctk.CTkFont(
                    family=FONT_BODY,
                    size=12
                )
            )

            label.pack(
                anchor="w",
                pady=8
            )


        # =================================================
        # RIGHT SIDE
        # =================================================

        self.right_frame = ctk.CTkFrame(
            self.main_frame,
            fg_color=WHITE,
            corner_radius=0
        )

        self.right_frame.grid(
            row=0,
            column=1,
            sticky="nsew",
            padx=35,
            pady=30
        )


        # =================================================
        # TABS
        # =================================================

        self.tabs_frame = ctk.CTkFrame(
            self.right_frame,
            fg_color="#F4EFE5",
            corner_radius=10,
            height=50
        )

        self.tabs_frame.pack(
            fill="x",
            pady=(0, 25)
        )


        self.login_tab = ctk.CTkButton(
            self.tabs_frame,
            text="Login",
            height=40,
            corner_radius=8,
            fg_color=WHITE,
            hover_color="#FBF8F2",
            text_color=PRIMARY,
            font=ctk.CTkFont(
                family=FONT_BODY,
                size=13,
                weight="bold"
            ),
            command=self.show_login
        )

        self.login_tab.pack(
            side="left",
            fill="x",
            expand=True,
            padx=(5, 2),
            pady=5
        )


        self.signup_tab = ctk.CTkButton(
            self.tabs_frame,
            text="Sign Up",
            height=40,
            corner_radius=8,
            fg_color="transparent",
            hover_color="#F1EADB",
            text_color=TEXT_LIGHT,
            font=ctk.CTkFont(
                family=FONT_BODY,
                size=13,
                weight="bold"
            ),
            command=self.show_signup
        )

        self.signup_tab.pack(
            side="right",
            fill="x",
            expand=True,
            padx=(2, 5),
            pady=5
        )


        # =================================================
        # FORM AREA
        # =================================================

        self.form_frame = ctk.CTkScrollableFrame(
            self.right_frame,
            fg_color=WHITE
        )

        self.form_frame.pack(
            fill="both",
            expand=True
        )


    # =====================================================
    # CLEAR FORM
    # =====================================================

    def clear_form(self):

        for widget in self.form_frame.winfo_children():
            widget.destroy()


    # =====================================================
    # SHOW LOGIN
    # =====================================================

    def show_login(self):

        self.clear_form()

        self.login_tab.configure(
            fg_color=WHITE,
            text_color=PRIMARY
        )

        self.signup_tab.configure(
            fg_color="transparent",
            text_color=TEXT_LIGHT
        )


        title = ctk.CTkLabel(
            self.form_frame,
            text="Welcome Back 👋",
            text_color=TEXT,
            font=ctk.CTkFont(
                family=FONT_HEAD,
                size=24,
                weight="bold"
            )
        )

        title.pack(
            anchor="w",
            pady=(0, 5)
        )


        subtitle = ctk.CTkLabel(
            self.form_frame,
            text="Login to your Smart Attendance account",
            text_color=TEXT_LIGHT,
            font=ctk.CTkFont(
                family=FONT_BODY,
                size=12
            )
        )

        subtitle.pack(
            anchor="w",
            pady=(0, 20)
        )


        self.login_email = self.create_entry(
            "Email Address",
            "example@gmail.com"
        )


        self.login_password = self.create_password(
            "Password",
            "Enter your password"
        )


        self.remember_var = ctk.BooleanVar(
            value=False
        )


        remember = ctk.CTkCheckBox(
            self.form_frame,
            text="Remember me",
            variable=self.remember_var,
            fg_color=PRIMARY,
            hover_color=PRIMARY_LIGHT,
            text_color=TEXT_LIGHT,
            font=ctk.CTkFont(
                family=FONT_BODY,
                size=11
            )
        )

        remember.pack(
            anchor="w",
            pady=(5, 20)
        )


        login_button = ctk.CTkButton(
            self.form_frame,
            text="Login",
            height=45,
            corner_radius=9,
            fg_color=PRIMARY,
            hover_color=PRIMARY_LIGHT,
            font=ctk.CTkFont(
                family=FONT_BODY,
                size=13,
                weight="bold"
            ),
            command=self.login_user
        )

        login_button.pack(
            fill="x"
        )


        bottom = ctk.CTkLabel(
            self.form_frame,
            text="Don't have an account?  Create Account",
            text_color=TEXT_LIGHT,
            cursor="hand2",
            font=ctk.CTkFont(
                family=FONT_BODY,
                size=11
            )
        )

        bottom.pack(
            pady=20
        )

        bottom.bind(
            "<Button-1>",
            lambda event: self.show_signup()
        )


    # =====================================================
    # SHOW SIGNUP
    # =====================================================

    def show_signup(self):

        self.clear_form()

        self.signup_tab.configure(
            fg_color=WHITE,
            text_color=PRIMARY
        )

        self.login_tab.configure(
            fg_color="transparent",
            text_color=TEXT_LIGHT
        )


        title = ctk.CTkLabel(
            self.form_frame,
            text="Create Account",
            text_color=TEXT,
            font=ctk.CTkFont(
                family=FONT_HEAD,
                size=24,
                weight="bold"
            )
        )

        title.pack(
            anchor="w",
            pady=(0, 5)
        )


        subtitle = ctk.CTkLabel(
            self.form_frame,
            text="Register for Smart Attendance",
            text_color=TEXT_LIGHT,
            font=ctk.CTkFont(
                family=FONT_BODY,
                size=12
            )
        )

        subtitle.pack(
            anchor="w",
            pady=(0, 18)
        )


        self.full_name = self.create_entry(
            "Full Name",
            "Enter full name"
        )


        self.user_id = self.create_entry(
            "Student/Staff ID",
            "Example: STU1024"
        )


        self.signup_email = self.create_entry(
            "Email Address",
            "example@gmail.com"
        )


        self.role = self.create_option(
            "Role",
            [
                "Select Role",
                "Student",
                "Faculty",
                "Admin"
            ]
        )


        self.department = self.create_option(
            "Department",
            [
                "Select Department",
                "Computer Science",
                "Information Technology",
                "Electronics",
                "Mechanical",
                "Civil"
            ]
        )


        self.signup_password = self.create_password(
            "Password",
            "Create password"
        )


        self.confirm_password = self.create_password(
            "Confirm Password",
            "Confirm password"
        )


        self.terms_var = ctk.BooleanVar(
            value=False
        )


        terms = ctk.CTkCheckBox(
            self.form_frame,
            text="I agree to Terms & Privacy Policy",
            variable=self.terms_var,
            fg_color=PRIMARY,
            hover_color=PRIMARY_LIGHT,
            text_color=TEXT_LIGHT,
            font=ctk.CTkFont(
                family=FONT_BODY,
                size=11
            )
        )

        terms.pack(
            anchor="w",
            pady=(5, 18)
        )


        signup_button = ctk.CTkButton(
            self.form_frame,
            text="Create Account",
            height=45,
            corner_radius=9,
            fg_color=PRIMARY,
            hover_color=PRIMARY_LIGHT,
            font=ctk.CTkFont(
                family=FONT_BODY,
                size=13,
                weight="bold"
            ),
            command=self.signup_user
        )

        signup_button.pack(
            fill="x"
        )


        bottom = ctk.CTkLabel(
            self.form_frame,
            text="Already have an account?  Login",
            text_color=TEXT_LIGHT,
            cursor="hand2",
            font=ctk.CTkFont(
                family=FONT_BODY,
                size=11
            )
        )

        bottom.pack(
            pady=18
        )

        bottom.bind(
            "<Button-1>",
            lambda event: self.show_login()
        )


    # =====================================================
    # CREATE ENTRY
    # =====================================================

    def create_entry(
        self,
        label_text,
        placeholder
    ):

        label = ctk.CTkLabel(
            self.form_frame,
            text=label_text,
            text_color=TEXT,
            font=ctk.CTkFont(
                family=FONT_BODY,
                size=11,
                weight="bold"
            )
        )

        label.pack(
            anchor="w",
            pady=(5, 5)
        )


        entry = ctk.CTkEntry(
            self.form_frame,
            height=42,
            placeholder_text=placeholder,
            border_color=BORDER,
            fg_color=WHITE,
            text_color=TEXT,
            corner_radius=9
        )

        entry.pack(
            fill="x",
            pady=(0, 8)
        )

        return entry


    # =====================================================
    # CREATE PASSWORD
    # =====================================================

    def create_password(
        self,
        label_text,
        placeholder
    ):

        label = ctk.CTkLabel(
            self.form_frame,
            text=label_text,
            text_color=TEXT,
            font=ctk.CTkFont(
                family=FONT_BODY,
                size=11,
                weight="bold"
            )
        )

        label.pack(
            anchor="w",
            pady=(5, 5)
        )


        frame = ctk.CTkFrame(
            self.form_frame,
            fg_color="transparent"
        )

        frame.pack(
            fill="x",
            pady=(0, 8)
        )


        entry = ctk.CTkEntry(
            frame,
            height=42,
            placeholder_text=placeholder,
            border_color=BORDER,
            fg_color=WHITE,
            text_color=TEXT,
            corner_radius=9,
            show="*"
        )

        entry.pack(
            side="left",
            fill="x",
            expand=True
        )


        show_button = ctk.CTkButton(
            frame,
            text="👁",
            width=40,
            height=40,
            fg_color="transparent",
            hover_color="#F4EFE5",
            text_color=PRIMARY,
            command=lambda: self.toggle_password(
                entry,
                show_button
            )
        )

        show_button.place(
            relx=1,
            x=-4,
            y=1,
            anchor="ne"
        )

        return entry


    # =====================================================
    # CREATE OPTION
    # =====================================================

    def create_option(
        self,
        label_text,
        values
    ):

        label = ctk.CTkLabel(
            self.form_frame,
            text=label_text,
            text_color=TEXT,
            font=ctk.CTkFont(
                family=FONT_BODY,
                size=11,
                weight="bold"
            )
        )

        label.pack(
            anchor="w",
            pady=(5, 5)
        )


        option = ctk.CTkOptionMenu(
            self.form_frame,
            values=values,
            height=42,
            fg_color=WHITE,
            button_color=PRIMARY,
            button_hover_color=PRIMARY_LIGHT,
            text_color=TEXT,
            dropdown_fg_color=WHITE,
            dropdown_text_color=TEXT,
            corner_radius=9
        )

        option.set(values[0])

        option.pack(
            fill="x",
            pady=(0, 8)
        )

        return option


    # =====================================================
    # PASSWORD SHOW/HIDE
    # =====================================================

    def toggle_password(
        self,
        entry,
        button
    ):

        if entry.cget("show") == "*":

            entry.configure(
                show=""
            )

            button.configure(
                text="🙈"
            )

        else:

            entry.configure(
                show="*"
            )

            button.configure(
                text="👁"
            )


    # =====================================================
    # LOGIN
    # =====================================================

    def login_user(self):

        email = self.login_email.get().strip()
        password = self.login_password.get()


        if email == "":

            messagebox.showerror(
                "Validation Error",
                "Email is required."
            )

            return


        if not valid_email(email):

            messagebox.showerror(
                "Validation Error",
                "Enter a valid email address."
            )

            return


        if password == "":

            messagebox.showerror(
                "Validation Error",
                "Password is required."
            )

            return


        users = load_users()

        password_hash = hash_password(
            password
        )


        for user in users:

            stored_email = str(
                user.get("email", "")
            ).strip()

            stored_password = str(
                user.get("password", "")
            )


            if (
                stored_email.lower() == email.lower()
                and stored_password == password_hash
            ):

                messagebox.showinfo(
                    "Login Successful",
                    f"Welcome, {user.get('full_name', 'User')}!"
                )

                self.open_main_application(user)

                return


        messagebox.showerror(
            "Login Failed",
            "Invalid email or password."
        )


    # =====================================================
    # OPEN MAIN APPLICATION
    # =====================================================

    def open_main_application(self, user=None):

        if not os.path.exists(MAIN_FILE):

            messagebox.showerror(
                "Main Application Not Found",
                (
                    "Login successful, but main.py was not found.\n\n"
                    f"Expected location:\n{MAIN_FILE}"
                )
            )

            return


        try:

            # hand the signed-in account to the next window
            env = os.environ.copy()

            if user:

                env["SMARTMARK_USER_ID"] = str(user.get("user_id", ""))
                env["SMARTMARK_USER_NAME"] = str(user.get("full_name", ""))
                env["SMARTMARK_USER_ROLE"] = str(user.get("role", ""))
                env["SMARTMARK_USER_DEPT"] = str(user.get("department", ""))

            subprocess.Popen(
                [
                    sys.executable,
                    MAIN_FILE
                ],
                cwd=BASE_DIR,
                env=env
            )

            self.destroy()


        except Exception as error:

            messagebox.showerror(
                "Launch Error",
                f"Could not open main.py.\n\n{error}"
            )


    # =====================================================
    # SIGN UP
    # =====================================================

    def signup_user(self):

        name = self.full_name.get().strip()

        user_id = self.user_id.get().strip()

        email = self.signup_email.get().strip()

        role = self.role.get()

        department = self.department.get()

        password = self.signup_password.get()

        confirm_password = self.confirm_password.get()


        # =================================================
        # NAME
        # =================================================

        if name == "":

            messagebox.showerror(
                "Validation Error",
                "Full name is required."
            )

            return


        if not valid_name(name):

            messagebox.showerror(
                "Validation Error",
                "Enter a valid name using letters and spaces only."
            )

            return


        # =================================================
        # USER ID
        # =================================================

        if user_id == "":

            messagebox.showerror(
                "Validation Error",
                "Student/Staff ID is required."
            )

            return


        if not valid_user_id(user_id):

            messagebox.showerror(
                "Validation Error",
                "ID must contain 3-20 letters, numbers, _ or -."
            )

            return


        # =================================================
        # EMAIL
        # =================================================

        if email == "":

            messagebox.showerror(
                "Validation Error",
                "Email is required."
            )

            return


        if not valid_email(email):

            messagebox.showerror(
                "Validation Error",
                "Enter a valid email address."
            )

            return


        # =================================================
        # ROLE
        # =================================================

        if role == "Select Role":

            messagebox.showerror(
                "Validation Error",
                "Please select a role."
            )

            return


        # =================================================
        # DEPARTMENT
        # =================================================

        if department == "Select Department":

            messagebox.showerror(
                "Validation Error",
                "Please select a department."
            )

            return


        # =================================================
        # PASSWORD
        # =================================================

        if password == "":

            messagebox.showerror(
                "Validation Error",
                "Password is required."
            )

            return


        if not valid_password(password):

            messagebox.showerror(
                "Validation Error",
                (
                    "Password must contain:\n\n"
                    "• Minimum 8 characters\n"
                    "• At least one letter\n"
                    "• At least one number\n"
                    "• At least one special character"
                )
            )

            return


        # =================================================
        # CONFIRM PASSWORD
        # =================================================

        if confirm_password == "":

            messagebox.showerror(
                "Validation Error",
                "Please confirm your password."
            )

            return


        if password != confirm_password:

            messagebox.showerror(
                "Validation Error",
                "Passwords do not match."
            )

            return


        # =================================================
        # TERMS
        # =================================================

        if not self.terms_var.get():

            messagebox.showerror(
                "Validation Error",
                "You must accept the Terms & Privacy Policy."
            )

            return


        # =================================================
        # CHECK DUPLICATE USER
        # =================================================

        users = load_users()


        for user in users:

            existing_email = str(
                user.get("email", "")
            ).strip()

            existing_user_id = str(
                user.get("user_id", "")
            ).strip()


            if existing_email.lower() == email.lower():

                messagebox.showerror(
                    "Registration Error",
                    "This email is already registered."
                )

                return


            if existing_user_id.lower() == user_id.lower():

                messagebox.showerror(
                    "Registration Error",
                    "This Student/Staff ID already exists."
                )

                return


        # =================================================
        # CREATE USER
        # =================================================

        new_user = {
            "full_name": name,
            "user_id": user_id,
            "email": email,
            "role": role,
            "department": department,
            "password": hash_password(password)
        }


        users.append(
            new_user
        )


        try:

            save_users(users)

        except OSError as error:

            messagebox.showerror(
                "Save Error",
                f"Could not save account.\n\n{error}"
            )

            return


        # =================================================
        # SUCCESS
        # =================================================

        messagebox.showinfo(
            "Registration Successful",
            (
                "Account created successfully!\n\n"
                "You can now login with your email and password."
            )
        )


        self.show_login()


# =========================================================
# START APPLICATION
# =========================================================

if __name__ == "__main__":

    app = SmartAttendanceLogin()

    app.mainloop()