import cv2
import customtkinter as ctk
from theme import *  # noqa: F401,F403
from face_capture import show_guidelines, capture_face
from PIL import Image
from tkinter import messagebox
import os
import re
import subprocess
import sys
import json
import csv
from datetime import datetime


# ============================================================
# PROJECT PATHS
# ============================================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

IMAGE_FOLDER = os.path.join(
    BASE_DIR,
    "student_images"
)

STUDENT_JSON = os.path.join(
    BASE_DIR,
    "students.json"
)

STUDENT_CSV = os.path.join(
    BASE_DIR,
    "students.csv"
)


# ============================================================
# CREATE REQUIRED FOLDER
# ============================================================

try:
    os.makedirs(
        IMAGE_FOLDER,
        exist_ok=True
    )
except Exception as error:
    print("Unable to create student_images folder:", error)


# ============================================================
# CREATE JSON FILE
# ============================================================

if not os.path.exists(STUDENT_JSON):

    try:
        with open(
            STUDENT_JSON,
            "w",
            encoding="utf-8"
        ) as file:

            json.dump(
                [],
                file,
                indent=4,
                ensure_ascii=False
            )

    except Exception as error:

        print(
            "Unable to create students.json:",
            error
        )


# ============================================================
# CREATE CSV FILE
# ============================================================

CSV_HEADERS = [
    "student_id",
    "prn",
    "name",
    "department",
    "class",
    "division",
    "email",
    "mobile",
    "photo",
    "registered_date"
]


if not os.path.exists(STUDENT_CSV):

    try:

        with open(
            STUDENT_CSV,
            "w",
            newline="",
            encoding="utf-8"
        ) as file:

            writer = csv.DictWriter(
                file,
                fieldnames=CSV_HEADERS
            )

            writer.writeheader()

    except Exception as error:

        print(
            "Unable to create students.csv:",
            error
        )


# ============================================================
# PRINT STORAGE INFORMATION
# ============================================================

print("=" * 70)
print("SmartMark")
print("=" * 70)

print("MAIN.PY:")
print(BASE_DIR)

print()

print("STUDENT JSON:")
print(STUDENT_JSON)

print()

print("STUDENT CSV:")
print(STUDENT_CSV)

print()

print("STUDENT IMAGES:")
print(IMAGE_FOLDER)

print("=" * 70)


# ============================================================
# THEME
# ============================================================



# ============================================================
# COLORS
# ============================================================
















# ============================================================
# APPLICATION
# ============================================================

app = ctk.CTk(
    fg_color=BG_COLOR
)

app.title(
    "AI-Based Smart Attendance System"
)

app.geometry(
    "1200x800"
)

app.resizable(
    True,
    True
)
app.minsize(980, 620)
maximize(app)

fade_in(app)


# ============================================================
# GLOBAL VARIABLES
# ============================================================

captured_image = None

captured_image_path = None


# ============================================================
# VALIDATION FUNCTIONS
# ============================================================

def valid_student_id(value):

    return bool(
        re.fullmatch(
            r"[A-Za-z0-9]{2,20}",
            value
        )
    )


def valid_prn(value):

    return bool(
        re.fullmatch(
            r"[0-9]{8,20}",
            value
        )
    )


def valid_name(value):

    return bool(
        re.fullmatch(
            r"[A-Za-z ]{2,50}",
            value
        )
    )


def valid_department(value):

    return bool(
        re.fullmatch(
            r"[A-Za-z .&-]{2,60}",
            value
        )
    )


def valid_mobile(value):

    return bool(
        re.fullmatch(
            r"[6-9][0-9]{9}",
            value
        )
    )


def valid_email(value):

    pattern = (
        r"^[A-Za-z0-9._%+-]+"
        r"@[A-Za-z0-9.-]+"
        r"\.[A-Za-z]{2,}$"
    )

    return bool(
        re.fullmatch(
            pattern,
            value
        )
    )


# ============================================================
# LOAD STUDENTS FROM JSON
# ============================================================

def load_students():

    try:

        if not os.path.exists(
            STUDENT_JSON
        ):

            with open(
                STUDENT_JSON,
                "w",
                encoding="utf-8"
            ) as file:

                json.dump(
                    [],
                    file,
                    indent=4
                )

            return []


        with open(
            STUDENT_JSON,
            "r",
            encoding="utf-8"
        ) as file:

            data = json.load(file)


        if isinstance(
            data,
            list
        ):

            return data


        return []


    except json.JSONDecodeError:

        messagebox.showerror(
            "JSON Error",
            "students.json contains invalid data."
        )

        return []


    except Exception as error:

        messagebox.showerror(
            "File Error",
            f"Unable to read students.json.\n\n{error}"
        )

        return []


# ============================================================
# SAVE JSON
# ============================================================

def save_json(students):

    try:

        with open(
            STUDENT_JSON,
            "w",
            encoding="utf-8"
        ) as file:

            json.dump(
                students,
                file,
                indent=4,
                ensure_ascii=False
            )

        return True


    except Exception as error:

        messagebox.showerror(
            "JSON Save Error",
            f"Unable to save students.json.\n\n{error}"
        )

        return False


# ============================================================
# SAVE CSV
# ============================================================

def save_csv(students):

    try:

        with open(
            STUDENT_CSV,
            "w",
            newline="",
            encoding="utf-8"
        ) as file:

            writer = csv.DictWriter(
                file,
                fieldnames=CSV_HEADERS
            )

            writer.writeheader()

            for student in students:

                writer.writerow({

                    "student_id":
                        student.get(
                            "student_id",
                            ""
                        ),

                    "prn":
                        student.get(
                            "prn",
                            ""
                        ),

                    "name":
                        student.get(
                            "name",
                            ""
                        ),

                    "department":
                        student.get(
                            "department",
                            ""
                        ),

                    "class":
                        student.get(
                            "class",
                            ""
                        ),

                    "division":
                        student.get(
                            "division",
                            ""
                        ),

                    "email":
                        student.get(
                            "email",
                            ""
                        ),

                    "mobile":
                        student.get(
                            "mobile",
                            ""
                        ),

                    "photo":
                        student.get(
                            "photo",
                            ""
                        ),

                    "registered_date":
                        student.get(
                            "registered_date",
                            ""
                        )
                })


        return True


    except Exception as error:

        messagebox.showerror(
            "CSV Save Error",
            f"Unable to save students.csv.\n\n{error}"
        )

        return False


# ============================================================
# SAVE STUDENT
# ============================================================

def save_student_data(student):

    students = load_students()

    students.append(
        student
    )

    json_saved = save_json(
        students
    )

    if not json_saved:

        return False


    csv_saved = save_csv(
        students
    )

    if not csv_saved:

        return False


    print()
    print("=" * 70)
    print("STUDENT SAVED SUCCESSFULLY")
    print("=" * 70)

    print(
        "Student ID:",
        student["student_id"]
    )

    print(
        "PRN:",
        student["prn"]
    )

    print(
        "Name:",
        student["name"]
    )

    print(
        "Department:",
        student["department"]
    )

    print(
        "Class:",
        student["class"]
    )

    print(
        "Division:",
        student["division"]
    )

    print(
        "Email:",
        student["email"]
    )

    print(
        "Mobile:",
        student["mobile"]
    )

    print(
        "Photo:",
        student["photo"]
    )

    print(
        "JSON:",
        STUDENT_JSON
    )

    print(
        "CSV:",
        STUDENT_CSV
    )

    print("=" * 70)

    return True


# ============================================================
# CREATE SAFE PHOTO FILE NAME
# ============================================================

def create_safe_filename(
    student_id,
    student_name
):

    safe_name = re.sub(
        r"[^A-Za-z0-9]+",
        "_",
        student_name
    ).strip("_")


    if safe_name == "":
        safe_name = "student"


    return (
        f"{student_id}_{safe_name}.jpg"
    )


# ============================================================
# DISPLAY CAPTURED IMAGE
# ============================================================

def display_captured_image(
    frame
):

    try:

        frame_rgb = cv2.cvtColor(
            frame,
            cv2.COLOR_BGR2RGB
        )

        image = Image.fromarray(
            frame_rgb
        )

        image.thumbnail(
            (
                350,
                285
            )
        )

        photo = ctk.CTkImage(
            light_image=image,
            dark_image=image,
            size=image.size
        )

        image_label.configure(
            image=photo,
            text=""
        )

        image_label.image = photo


    except Exception as error:

        print(
            "Image display error:",
            error
        )


# ============================================================
# OPEN CAMERA
# ============================================================

def open_attendance_dashboard():

    dashboard = os.path.join(
        BASE_DIR,
        "attendance_dashboard.py"
    )

    if not os.path.exists(dashboard):

        messagebox.showerror(
            "File Not Found",
            "attendance_dashboard.py was not found."
        )

        return

    try:

        # the signed-in faculty identity is inherited through the environment
        subprocess.Popen(
            [sys.executable, dashboard],
            cwd=BASE_DIR
        )
        app.destroy()

    except Exception as error:

        messagebox.showerror(
            "Unable to Open Attendance",
            str(error)
        )


# ============================================================
# OPEN CAMERA
# ============================================================

def open_camera():

    global captured_image
    global captured_image_path


    student_id = id_entry.get().strip()

    student_name = name_entry.get().strip()


    # --------------------------------------------------------
    # CHECK STUDENT ID
    # --------------------------------------------------------

    if student_id == "":

        messagebox.showwarning(
            "Missing Information",
            "Please enter Student ID first."
        )

        id_entry.focus()

        return


    if not valid_student_id(
        student_id
    ):

        messagebox.showwarning(
            "Invalid Student ID",
            "Student ID should contain only "
            "letters and numbers."
        )

        id_entry.focus()

        return


    # --------------------------------------------------------
    # CHECK NAME
    # --------------------------------------------------------

    if student_name == "":

        messagebox.showwarning(
            "Missing Information",
            "Please enter Student Name first."
        )

        name_entry.focus()

        return


    if not valid_name(
        student_name
    ):

        messagebox.showwarning(
            "Invalid Name",
            "Student Name should contain "
            "letters and spaces only."
        )

        name_entry.focus()

        return


    # --------------------------------------------------------
    # CHECK DUPLICATE ID
    # --------------------------------------------------------

    students = load_students()


    for student in students:

        if (
            str(
                student.get(
                    "student_id",
                    ""
                )
            ).lower()
            ==
            student_id.lower()
        ):

            messagebox.showerror(
                "Duplicate Student ID",
                "This Student ID is already registered."
            )

            return


    # --------------------------------------------------------
    # PHOTO GUIDELINES (must be accepted before the camera opens)
    # --------------------------------------------------------

    if not show_guidelines(
        app,
        student_name
    ):

        status_label.configure(
            text="Photo capture cancelled",
            text_color=MUTED_TEXT
        )

        return


    # --------------------------------------------------------
    # GUIDED CAPTURE
    # --------------------------------------------------------

    try:

        frame = capture_face(
            student_name
        )

    except RuntimeError:

        messagebox.showerror(
            "Camera Error",
            "Unable to open or read the camera.\n\n"
            "Please check your camera connection "
            "and camera permissions."
        )

        return

    except Exception as error:

        messagebox.showerror(
            "Camera Window Error",
            "The camera window could not be displayed.\n\n"
            f"{type(error).__name__}: {error}\n\n"
            "Try:  pip uninstall opencv-python  then  "
            "pip install opencv-python==4.10.0.84"
        )

        return


    if frame is None:

        status_label.configure(
            text="Photo capture cancelled",
            text_color=MUTED_TEXT
        )

        return


    captured_image = frame.copy()

    filename = create_safe_filename(
        student_id,
        student_name
    )

    captured_image_path = os.path.join(
        IMAGE_FOLDER,
        filename
    )

    if not cv2.imwrite(
        captured_image_path,
        captured_image
    ):

        captured_image_path = None

        messagebox.showerror(
            "Photo Error",
            "Unable to save student photo."
        )

        return


    display_captured_image(
        captured_image
    )

    photo_status.configure(
        text="✓ Face Photo Verified & Captured",
        text_color=SUCCESS
    )

    status_label.configure(
        text="Photo captured successfully",
        text_color=SUCCESS
    )

    messagebox.showinfo(
        "Photo Captured",
        "Student photo captured successfully!\n\n"
        f"Saved as:\n{filename}"
    )


# ============================================================
# CLEAR FORM
# ============================================================

def clear_form():

    global captured_image
    global captured_image_path


    id_entry.delete(
        0,
        "end"
    )

    prn_entry.delete(
        0,
        "end"
    )

    name_entry.delete(
        0,
        "end"
    )

    department_entry.delete(
        0,
        "end"
    )

    email_entry.delete(
        0,
        "end"
    )

    mobile_entry.delete(
        0,
        "end"
    )


    class_dropdown.set(
        "Select Class"
    )

    division_dropdown.set(
        "Select Division"
    )


    image_label.configure(
        image=None,
        text="📷\n\nNo Photo Captured",
        text_color=MUTED_TEXT
    )

    image_label.image = None


    photo_status.configure(
        text="No Photo Captured",
        text_color=MUTED_TEXT
    )


    status_label.configure(
        text="Ready for Registration",
        text_color=MUTED_TEXT
    )


    captured_image = None

    captured_image_path = None


# ============================================================
# REGISTER STUDENT
# ============================================================

def register_student():

    global captured_image_path


    # --------------------------------------------------------
    # GET VALUES
    # --------------------------------------------------------

    student_id = id_entry.get().strip()

    prn = prn_entry.get().strip()

    student_name = name_entry.get().strip()

    department = department_entry.get().strip()

    student_class = class_dropdown.get().strip()

    division = division_dropdown.get().strip()

    email = email_entry.get().strip()

    mobile = mobile_entry.get().strip()


    # ========================================================
    # STUDENT ID
    # ========================================================

    if student_id == "":

        messagebox.showwarning(
            "Required",
            "Please enter Student ID."
        )

        id_entry.focus()

        return


    if not valid_student_id(
        student_id
    ):

        messagebox.showwarning(
            "Invalid Student ID",
            "Student ID must contain only "
            "letters and numbers."
        )

        id_entry.focus()

        return


    # ========================================================
    # PRN
    # ========================================================

    if prn == "":

        messagebox.showwarning(
            "Required",
            "Please enter PRN Number."
        )

        prn_entry.focus()

        return


    if not valid_prn(
        prn
    ):

        messagebox.showwarning(
            "Invalid PRN",
            "PRN must contain 8 to 20 digits."
        )

        prn_entry.focus()

        return


    # ========================================================
    # NAME
    # ========================================================

    if student_name == "":

        messagebox.showwarning(
            "Required",
            "Please enter Student Name."
        )

        name_entry.focus()

        return


    if not valid_name(
        student_name
    ):

        messagebox.showwarning(
            "Invalid Name",
            "Student Name should contain "
            "letters and spaces only."
        )

        name_entry.focus()

        return


    # ========================================================
    # DEPARTMENT
    # ========================================================

    if department == "":

        messagebox.showwarning(
            "Required",
            "Please enter Department."
        )

        department_entry.focus()

        return


    if not valid_department(
        department
    ):

        messagebox.showwarning(
            "Invalid Department",
            "Department contains invalid characters."
        )

        department_entry.focus()

        return


    # ========================================================
    # CLASS
    # ========================================================

    if student_class == "Select Class":

        messagebox.showwarning(
            "Required",
            "Please select Class."
        )

        return


    # ========================================================
    # DIVISION
    # ========================================================

    if division == "Select Division":

        messagebox.showwarning(
            "Required",
            "Please select Division."
        )

        return


    # ========================================================
    # EMAIL
    # ========================================================

    if email == "":

        messagebox.showwarning(
            "Required",
            "Please enter Email."
        )

        email_entry.focus()

        return


    if not valid_email(
        email
    ):

        messagebox.showwarning(
            "Invalid Email",
            "Please enter a valid email address.\n\n"
            "Example: student@gmail.com"
        )

        email_entry.focus()

        return


    # ========================================================
    # MOBILE
    # ========================================================

    if mobile == "":

        messagebox.showwarning(
            "Required",
            "Please enter Mobile Number."
        )

        mobile_entry.focus()

        return


    if not valid_mobile(
        mobile
    ):

        messagebox.showwarning(
            "Invalid Mobile",
            "Please enter a valid 10-digit mobile number."
        )

        mobile_entry.focus()

        return


    # ========================================================
    # PHOTO
    # ========================================================

    if captured_image_path is None:

        messagebox.showwarning(
            "Photo Required",
            "Please capture the student's face photo "
            "before registering."
        )

        return


    if not os.path.exists(
        captured_image_path
    ):

        messagebox.showerror(
            "Photo Error",
            "Captured photo could not be found.\n\n"
            "Please capture the photo again."
        )

        captured_image_path = None

        return


    # ========================================================
    # LOAD EXISTING STUDENTS
    # ========================================================

    students = load_students()


    # ========================================================
    # DUPLICATE CHECKS
    # ========================================================

    for student in students:

        existing_id = str(
            student.get(
                "student_id",
                ""
            )
        ).lower()


        existing_prn = str(
            student.get(
                "prn",
                ""
            )
        )


        existing_email = str(
            student.get(
                "email",
                ""
            )
        ).lower()


        existing_mobile = str(
            student.get(
                "mobile",
                ""
            )
        )


        if existing_id == student_id.lower():

            messagebox.showerror(
                "Duplicate Student ID",
                "This Student ID is already registered."
            )

            return


        if existing_prn == prn:

            messagebox.showerror(
                "Duplicate PRN",
                "This PRN Number is already registered."
            )

            return


        if existing_email == email.lower():

            messagebox.showerror(
                "Duplicate Email",
                "This email address is already registered."
            )

            return


        if existing_mobile == mobile:

            messagebox.showerror(
                "Duplicate Mobile",
                "This mobile number is already registered."
            )

            return


    # ========================================================
    # STUDENT DATA
    # ========================================================

    student_data = {

        "student_id":
            student_id,

        "prn":
            prn,

        "name":
            student_name,

        "department":
            department,

        "class":
            student_class,

        "division":
            division,

        "email":
            email,

        "mobile":
            mobile,

        "photo":
            os.path.abspath(
                captured_image_path
            ),

        "registered_date":
            datetime.now().strftime(
                "%Y-%m-%d %H:%M:%S"
            )
    }


    # ========================================================
    # SAVE JSON + CSV
    # ========================================================

    saved = save_student_data(
        student_data
    )


    if not saved:

        return


    # ========================================================
    # SUCCESS
    # ========================================================

    status_label.configure(
        text="✓ Student Registered Successfully",
        text_color=SUCCESS
    )


    update_student_count()


    messagebox.showinfo(
        "Registration Successful",

        "Student registered successfully!\n\n"

        f"Student ID: {student_id}\n"
        f"PRN: {prn}\n"
        f"Name: {student_name}\n"
        f"Department: {department}\n"
        f"Class: {student_class}\n"
        f"Division: {division}\n"
        f"Email: {email}\n"
        f"Mobile: {mobile}\n\n"

        "✓ Details saved in students.json\n"
        "✓ Backup saved in students.csv\n"
        "✓ Face photo saved in student_images/"
    )


    clear_form()


# ============================================================
# UPDATE STUDENT COUNT
# ============================================================

def update_student_count():

    students = load_students()

    count = len(
        students
    )

    student_count_label.configure(
        text=f"Registered Students: {count}"
    )


# ============================================================
# VIEW REGISTERED STUDENTS
# ============================================================

def view_registered_students():

    students = load_students()


    if not students:

        messagebox.showinfo(
            "Registered Students",

            "No student registration data found.\n\n"

            f"JSON:\n{STUDENT_JSON}\n\n"

            f"CSV:\n{STUDENT_CSV}"
        )

        return


    # ========================================================
    # WINDOW
    # ========================================================

    window = ctk.CTkToplevel(
        app
    )

    window.title(
        "Registered Students"
    )

    window.geometry(
        "1150x680"
    )

    window.configure(
        fg_color=BG_COLOR
    )


    # ========================================================
    # HEADER
    # ========================================================

    header = ctk.CTkFrame(
        window,
        fg_color=INK,
        corner_radius=0,
        height=80
    )

    header.pack(
        fill="x"
    )

    header.pack_propagate(
        False
    )


    ctk.CTkLabel(
        header,
        text="👥 Registered Students",
        font=(
            FONT_HEAD,
            24,
            "bold"
        ),
        text_color=WHITE
    ).pack(
        side="left",
        padx=25
    )


    total_label = ctk.CTkLabel(
        header,
        text=f"Total: {len(students)}",
        font=(
            FONT_BODY,
            14,
            "bold"
        ),
        text_color=WHITE
    )

    total_label.pack(
        side="right",
        padx=25
    )


    # ========================================================
    # SEARCH FRAME
    # ========================================================

    search_frame = ctk.CTkFrame(
        window,
        fg_color="transparent"
    )

    search_frame.pack(
        fill="x",
        padx=25,
        pady=15
    )


    search_entry = ctk.CTkEntry(
        search_frame,
        width=500,
        height=42,
        corner_radius=10,
        placeholder_text=(
            "Search by ID, PRN, name, department..."
        ),
        border_color=BORDER_COLOR,
        border_width=2,
        fg_color=WHITE,
        text_color=TEXT_COLOR
    )

    search_entry.pack(
        side="left"
    )


    # ========================================================
    # TABLE
    # ========================================================

    table_frame = ctk.CTkFrame(
        window,
        fg_color=WHITE,
        corner_radius=15,
        border_width=2,
        border_color=BORDER_COLOR
    )

    table_frame.pack(
        fill="both",
        expand=True,
        padx=25,
        pady=(0, 20)
    )


    columns = [
        "Student ID",
        "PRN",
        "Name",
        "Department",
        "Class",
        "Division",
        "Mobile"
    ]


    widths = [
        110,
        130,
        190,
        180,
        90,
        90,
        130
    ]


    # ========================================================
    # TABLE HEADER
    # ========================================================

    header_row = ctk.CTkFrame(
        table_frame,
        fg_color=TINT,
        corner_radius=10
    )

    header_row.pack(
        fill="x",
        padx=8,
        pady=8
    )


    for index, column in enumerate(
        columns
    ):

        ctk.CTkLabel(
            header_row,
            text=column,
            width=widths[index],
            font=(
                FONT_BODY,
                11,
                "bold"
            ),
            text_color=INK
        ).grid(
            row=0,
            column=index,
            padx=2,
            pady=8
        )


    # ========================================================
    # SCROLL FRAME
    # ========================================================

    list_frame = ctk.CTkScrollableFrame(
        table_frame,
        fg_color=WHITE
    )

    list_frame.pack(
        fill="both",
        expand=True,
        padx=8,
        pady=(0, 8)
    )


    # ========================================================
    # STUDENT DETAILS
    # ========================================================

    def show_details(student):

        detail_window = ctk.CTkToplevel(
            window
        )

        detail_window.title(
            "Student Details"
        )

        detail_window.geometry(
            "900x620"
        )

        detail_window.configure(
            fg_color=BG_COLOR
        )


        # ----------------------------------------------------
        # LEFT INFORMATION
        # ----------------------------------------------------

        left = ctk.CTkFrame(
            detail_window,
            fg_color=WHITE,
            corner_radius=18,
            border_width=2,
            border_color=BORDER_COLOR
        )

        left.pack(
            side="left",
            fill="both",
            expand=True,
            padx=20,
            pady=20
        )


        ctk.CTkLabel(
            left,
            text="Student Information",
            font=(
                FONT_HEAD,
                23,
                "bold"
            ),
            text_color=INK
        ).pack(
            anchor="w",
            padx=25,
            pady=(25, 15)
        )


        details = (

            f"Student ID     : "
            f"{student.get('student_id', '')}\n\n"

            f"PRN            : "
            f"{student.get('prn', '')}\n\n"

            f"Name           : "
            f"{student.get('name', '')}\n\n"

            f"Department     : "
            f"{student.get('department', '')}\n\n"

            f"Class          : "
            f"{student.get('class', '')}\n\n"

            f"Division       : "
            f"{student.get('division', '')}\n\n"

            f"Email          : "
            f"{student.get('email', '')}\n\n"

            f"Mobile         : "
            f"{student.get('mobile', '')}\n\n"

            f"Registered     : "
            f"{student.get('registered_date', '')}"
        )


        ctk.CTkLabel(
            left,
            text=details,
            font=(
                FONT_BODY,
                13
            ),
            text_color=TEXT_COLOR,
            justify="left",
            anchor="w"
        ).pack(
            anchor="w",
            padx=25,
            pady=10
        )


        # ----------------------------------------------------
        # RIGHT PHOTO
        # ----------------------------------------------------

        right = ctk.CTkFrame(
            detail_window,
            width=330,
            fg_color=TINT,
            corner_radius=18,
            border_width=2,
            border_color=BORDER_COLOR
        )

        right.pack(
            side="right",
            fill="y",
            padx=(0, 20),
            pady=20
        )

        right.pack_propagate(
            False
        )


        ctk.CTkLabel(
            right,
            text="📸 Student Photo",
            font=(
                FONT_HEAD,
                20,
                "bold"
            ),
            text_color=INK
        ).pack(
            pady=(25, 15)
        )


        photo_path = student.get(
            "photo",
            ""
        )


        if os.path.exists(
            photo_path
        ):

            try:

                pil_image = Image.open(
                    photo_path
                )

                pil_image.thumbnail(
                    (
                        270,
                        320
                    )
                )


                student_photo = ctk.CTkImage(
                    light_image=pil_image,
                    dark_image=pil_image,
                    size=pil_image.size
                )


                photo_label = ctk.CTkLabel(
                    right,
                    image=student_photo,
                    text=""
                )

                photo_label.pack(
                    pady=15
                )

                photo_label.image = student_photo


            except Exception as error:

                ctk.CTkLabel(
                    right,
                    text=(
                        "Unable to load photo\n\n"
                        f"{error}"
                    ),
                    text_color=DANGER
                ).pack(
                    pady=50
                )


        else:

            ctk.CTkLabel(
                right,
                text="📷\n\nPhoto Not Found",
                font=(
                    FONT_BODY,
                    16,
                    "bold"
                ),
                text_color=MUTED_TEXT
            ).pack(
                pady=80
            )


    # ========================================================
    # REFRESH LIST
    # ========================================================

    def refresh_list():

        for widget in list_frame.winfo_children():

            widget.destroy()


        search_text = (
            search_entry
            .get()
            .strip()
            .lower()
        )


        filtered = []


        for student in students:

            searchable = " ".join(

                [
                    str(
                        student.get(
                            "student_id",
                            ""
                        )
                    ),

                    str(
                        student.get(
                            "prn",
                            ""
                        )
                    ),

                    str(
                        student.get(
                            "name",
                            ""
                        )
                    ),

                    str(
                        student.get(
                            "department",
                            ""
                        )
                    ),

                    str(
                        student.get(
                            "class",
                            ""
                        )
                    ),

                    str(
                        student.get(
                            "division",
                            ""
                        )
                    ),

                    str(
                        student.get(
                            "email",
                            ""
                        )
                    ),

                    str(
                        student.get(
                            "mobile",
                            ""
                        )
                    )
                ]

            ).lower()


            if (
                search_text == ""
                or
                search_text in searchable
            ):

                filtered.append(
                    student
                )


        if not filtered:

            ctk.CTkLabel(
                list_frame,
                text="No matching students found.",
                font=(
                    FONT_BODY,
                    14,
                    "bold"
                ),
                text_color=MUTED_TEXT
            ).pack(
                pady=40
            )

            return


        for student in filtered:

            row = ctk.CTkFrame(
                list_frame,
                fg_color=TINT,
                corner_radius=8
            )

            row.pack(
                fill="x",
                pady=3
            )


            values = [

                student.get(
                    "student_id",
                    ""
                ),

                student.get(
                    "prn",
                    ""
                ),

                student.get(
                    "name",
                    ""
                ),

                student.get(
                    "department",
                    ""
                ),

                student.get(
                    "class",
                    ""
                ),

                student.get(
                    "division",
                    ""
                ),

                student.get(
                    "mobile",
                    ""
                )
            ]


            for index, value in enumerate(
                values
            ):

                label = ctk.CTkLabel(
                    row,
                    text=str(value),
                    width=widths[index],
                    font=(
                        FONT_BODY,
                        10
                    ),
                    text_color=TEXT_COLOR,
                    anchor="center"
                )


                label.grid(
                    row=0,
                    column=index,
                    padx=2,
                    pady=10
                )


                label.bind(
                    "<Double-Button-1>",
                    lambda event,
                    s=student:
                    show_details(s)
                )


            row.bind(
                "<Double-Button-1>",
                lambda event,
                s=student:
                show_details(s)
            )


    search_entry.bind(
        "<KeyRelease>",
        lambda event:
        refresh_list()
    )


    refresh_list()


# ============================================================
# HEADER
# ============================================================

header_frame = ctk.CTkFrame(
    app,
    height=105,
    corner_radius=0,
    fg_color=INK
)

header_frame.pack(
    fill="x"
)

header_frame.pack_propagate(
    False
)

gold_rule(app, 3).pack(fill="x")


header_left = ctk.CTkFrame(
    header_frame,
    fg_color="transparent"
)

header_left.pack(
    side="left",
    padx=35,
    pady=15
)


ctk.CTkLabel(
    header_left,
    text="AI SMART ATTENDANCE",
    font=(
        FONT_HEAD,
        27,
        "bold"
    ),
    text_color=WHITE
).pack(
    anchor="w"
)


ctk.CTkLabel(
    header_left,
    text="Student Registration & Face Capture",
    font=(
        FONT_BODY,
        13
    ),
    text_color="#D9C28F"
).pack(
    anchor="w",
    pady=(3, 0)
)


# ============================================================
# HEADER BADGE
# ============================================================

ctk.CTkButton(
    header_frame,
    text="📋  Take Attendance",
    width=170,
    height=38,
    corner_radius=19,
    fg_color="transparent",
    border_width=1,
    border_color=GOLD,
    hover_color="#1E2C52",
    text_color=GOLD_LIGHT,
    font=(FONT_BODY, 12, "bold"),
    command=open_attendance_dashboard
).pack(
    side="right",
    padx=(0, 35)
)


ctk.CTkLabel(
    header_frame,
    text="● REGISTRATION",
    font=(
        FONT_BODY,
        12,
        "bold"
    ),
    text_color=INK,
    fg_color=GOLD_LIGHT,
    corner_radius=15,
    padx=15,
    pady=7
).pack(
    side="right",
    padx=(0, 14)
)


# ============================================================
# MAIN CARD
# ============================================================

main_frame = ctk.CTkScrollableFrame(
    app,
    fg_color=WHITE,
    corner_radius=22,
    border_width=2,
    border_color=BORDER_COLOR
)

main_frame.pack(
    padx=30,
    pady=20,
    fill="both",
    expand=True
)


# ============================================================
# LEFT FORM
# ============================================================

form_frame = ctk.CTkFrame(
    main_frame,
    fg_color="transparent"
)

form_frame.pack(
    side="left",
    padx=35,
    pady=15
)


ctk.CTkLabel(
    form_frame,
    text="Student Registration",
    font=(
        FONT_HEAD,
        22,
        "bold"
    ),
    text_color=INK
).pack(
    anchor="w",
    pady=(0, 2)
)


ctk.CTkLabel(
    form_frame,
    text="Enter student details below",
    font=(
        FONT_BODY,
        11
    ),
    text_color=MUTED_TEXT
).pack(
    anchor="w",
    pady=(0, 8)
)


# ============================================================
# ENTRY CREATOR
# ============================================================

ENTRY_WIDTH = 350

ENTRY_HEIGHT = 38


def create_entry(
    placeholder
):

    entry = ctk.CTkEntry(

        form_frame,

        width=ENTRY_WIDTH,

        height=ENTRY_HEIGHT,

        corner_radius=10,

        fg_color=WHITE,

        text_color=TEXT_COLOR,

        border_color=BORDER_COLOR,

        border_width=2,

        placeholder_text=placeholder,

        placeholder_text_color="#9B9486"
    )

    entry.pack(
        pady=3
    )

    return entry


# ============================================================
# FORM FIELDS
# ============================================================

id_entry = create_entry(
    "Student ID *"
)


prn_entry = create_entry(
    "PRN Number *"
)


name_entry = create_entry(
    "Student Name *"
)


department_entry = create_entry(
    "Department *"
)


# ============================================================
# CLASS
# ============================================================

class_dropdown = ctk.CTkComboBox(

    form_frame,

    width=ENTRY_WIDTH,

    height=ENTRY_HEIGHT,

    corner_radius=10,

    values=[
        "Select Class",
        "FY",
        "SY",
        "TY",
        "Final Year"
    ],

    fg_color=WHITE,

    text_color=TEXT_COLOR,

    border_color=BORDER_COLOR,

    button_color=PRIMARY,

    button_hover_color=PRIMARY_HOVER,

    dropdown_fg_color=WHITE,

    dropdown_hover_color=TINT,

    dropdown_text_color=TEXT_COLOR
)


class_dropdown.set(
    "Select Class"
)

class_dropdown.pack(
    pady=3
)


# ============================================================
# DIVISION
# ============================================================

division_dropdown = ctk.CTkComboBox(

    form_frame,

    width=ENTRY_WIDTH,

    height=ENTRY_HEIGHT,

    corner_radius=10,

    values=[
        "Select Division",
        "A",
        "B",
        "C",
        "D"
    ],

    fg_color=WHITE,

    text_color=TEXT_COLOR,

    border_color=BORDER_COLOR,

    button_color=PRIMARY,

    button_hover_color=PRIMARY_HOVER,

    dropdown_fg_color=WHITE,

    dropdown_hover_color=TINT,

    dropdown_text_color=TEXT_COLOR
)


division_dropdown.set(
    "Select Division"
)

division_dropdown.pack(
    pady=3
)


# ============================================================
# EMAIL
# ============================================================

email_entry = create_entry(
    "Email Address *"
)


# ============================================================
# MOBILE
# ============================================================

mobile_entry = create_entry(
    "Mobile Number *"
)


# ============================================================
# BUTTON FRAME
# ============================================================

button_frame = ctk.CTkFrame(
    form_frame,
    fg_color="transparent"
)

button_frame.pack(
    pady=7
)


# ============================================================
# CAPTURE BUTTON
# ============================================================

capture_button = ctk.CTkButton(

    button_frame,

    text="📷  Capture Face",

    width=170,

    height=40,

    corner_radius=10,

    fg_color=GOLD,

    hover_color=GOLD_LIGHT,

    text_color=INK,

    font=(
        FONT_BODY,
        12,
        "bold"
    ),

    command=open_camera
)

capture_button.grid(
    row=0,
    column=0,
    padx=5
)


# ============================================================
# CLEAR BUTTON
# ============================================================

clear_button = ctk.CTkButton(

    button_frame,

    text="↻  Clear",

    width=170,

    height=40,

    corner_radius=10,

    fg_color=LIGHT_GREY,

    hover_color="#E7E2D8",

    text_color=TEXT_COLOR,

    font=(
        FONT_BODY,
        12,
        "bold"
    ),

    command=clear_form
)

clear_button.grid(
    row=0,
    column=1,
    padx=5
)


# ============================================================
# REGISTER BUTTON
# ============================================================

register_button = ctk.CTkButton(

    form_frame,

    text="✓  REGISTER STUDENT",

    width=350,

    height=44,

    corner_radius=12,

    fg_color=GOLD,

    hover_color=GOLD_LIGHT,

    text_color=INK,

    font=(
        FONT_BODY,
        14,
        "bold"
    ),

    command=register_student
)

register_button.pack(
    pady=3
)


# ============================================================
# VIEW STUDENTS
# ============================================================

view_button = ctk.CTkButton(

    form_frame,

    text="👥  VIEW REGISTERED STUDENTS",

    width=350,

    height=40,

    corner_radius=12,

    fg_color=INK,

    hover_color="#24365C",

    text_color=WHITE,

    font=(
        FONT_BODY,
        12,
        "bold"
    ),

    command=view_registered_students
)

view_button.pack(
    pady=3
)


# ============================================================
# STUDENT COUNT
# ============================================================

student_count_label = ctk.CTkLabel(

    form_frame,

    text="Registered Students: 0",

    font=(
        FONT_BODY,
        11,
        "bold"
    ),

    text_color=PRIMARY
)

student_count_label.pack(
    pady=(2, 0)
)


# ============================================================
# STATUS
# ============================================================

status_label = ctk.CTkLabel(

    form_frame,

    text="Ready for Registration",

    font=(
        FONT_BODY,
        11,
        "bold"
    ),

    text_color=MUTED_TEXT
)

status_label.pack(
    pady=2
)


# ============================================================
# RIGHT PHOTO PANEL
# ============================================================

photo_frame = ctk.CTkFrame(

    main_frame,

    width=420,

    height=570,

    corner_radius=20,

    fg_color=TINT,

    border_width=2,

    border_color=BORDER_COLOR
)

photo_frame.pack(
    side="right",
    padx=30,
    pady=20
)

photo_frame.pack_propagate(
    False
)


# ============================================================
# PHOTO HEADING
# ============================================================

ctk.CTkLabel(

    photo_frame,

    text="📸  Student Face",

    font=(
        FONT_HEAD,
        22,
        "bold"
    ),

    text_color=INK
).pack(
    pady=(20, 3)
)


ctk.CTkLabel(

    photo_frame,

    text="Capture a clear front-facing photo",

    font=(
        FONT_BODY,
        12
    ),

    text_color=MUTED_TEXT
).pack(
    pady=(0, 10)
)


# ============================================================
# IMAGE AREA
# ============================================================

image_label = ctk.CTkLabel(

    photo_frame,

    text="📷\n\nNo Photo Captured",

    width=350,

    height=285,

    fg_color=WHITE,

    corner_radius=16,

    text_color=MUTED_TEXT,

    font=(
        FONT_BODY,
        15,
        "bold"
    )
)

image_label.pack(
    padx=25,
    pady=8
)


# ============================================================
# PHOTO STATUS
# ============================================================

photo_status = ctk.CTkLabel(

    photo_frame,

    text="No Photo Captured",

    font=(
        FONT_BODY,
        13,
        "bold"
    ),

    text_color=MUTED_TEXT
)

photo_status.pack(
    pady=5
)


# ============================================================
# INFORMATION BOX
# ============================================================

info_box = ctk.CTkFrame(

    photo_frame,

    fg_color=WHITE,

    corner_radius=12,

    border_width=1,

    border_color=BORDER_COLOR
)

info_box.pack(
    fill="x",
    padx=25,
    pady=8
)


ctk.CTkLabel(

    info_box,

    text="💡  Storage Information",

    font=(
        FONT_BODY,
        12,
        "bold"
    ),

    text_color=PRIMARY
).pack(
    anchor="w",
    padx=15,
    pady=(9, 3)
)


ctk.CTkLabel(

    info_box,

    text=
    "Student details → students.json\n"
    "Backup data → students.csv\n"
    "Face photos → student_images/",

    font=(
        FONT_BODY,
        11
    ),

    text_color=TEXT_COLOR,

    justify="left"
).pack(
    anchor="w",
    padx=15,
    pady=(0, 9)
)


# ============================================================
# INITIAL STUDENT COUNT
# ============================================================

update_student_count()


# ============================================================
# START APPLICATION
# ============================================================

print()
print("MAIN.PY IS RUNNING")
print()
print("Registration data will be stored in:")
print(STUDENT_JSON)
print()
print("Backup CSV will be stored in:")
print(STUDENT_CSV)
print()
print("Student photos will be stored in:")
print(IMAGE_FOLDER)
print()


app.mainloop()