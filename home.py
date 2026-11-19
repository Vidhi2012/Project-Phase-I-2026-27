import customtkinter as ctk
from theme import *  # noqa: F401,F403
from tkinter import messagebox
import subprocess
import sys
import os
import webbrowser


# =========================================================
# PROJECT PATH
# =========================================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MAIN_FILE = os.path.join(BASE_DIR, "main.py")


# =========================================================
# THEME
# =========================================================



# =========================================================
# COLORS
# =========================================================





# =========================================================
# MAIN WINDOW
# =========================================================

app = ctk.CTk(
    fg_color=BG_COLOR
)

app.title(
    "AI Smart Attendance System"
)

app.geometry(
    "1200x800"
)

app.minsize(
    1000,
    700
)
maximize(app)

fade_in(app)


# =========================================================
# OPEN REGISTRATION
# =========================================================

def open_registration():

    if not os.path.exists(MAIN_FILE):

        messagebox.showerror(
            "File Not Found",
            "main.py was not found.\n\n"
            "Please keep home.py and main.py "
            "in the same project folder."
        )

        return

    try:

        subprocess.Popen(
            [sys.executable, MAIN_FILE],
            cwd=BASE_DIR
        )
        app.destroy()

    except Exception as error:

        messagebox.showerror(
            "Unable to Open Registration",
            str(error)
        )



# =========================================================
# OPEN LOGIN HTML
# =========================================================

# =========================================================
# OPEN LOGIN PYTHON
# =========================================================

def open_login():

    login_file = os.path.join(BASE_DIR, "login.py")

    if not os.path.exists(login_file):

        messagebox.showerror(
            "File Not Found",
            "login.py was not found.\n\n"
            "Please keep home.py and login.py "
            "in the same project folder."
        )

        return

    try:

        subprocess.Popen(
            [sys.executable, login_file],
            cwd=BASE_DIR
        )
        app.destroy()

    except Exception as error:

        messagebox.showerror(
            "Unable to Open Login",
            str(error)
        )
# =========================================================
# EXIT APPLICATION
# =========================================================

def exit_application():

    answer = messagebox.askyesno(
        "Exit",
        "Are you sure you want to exit?"
    )

    if answer:
        app.destroy()


# =========================================================
# SCROLLABLE MAIN AREA
# =========================================================

main_scroll = ctk.CTkScrollableFrame(
    app,
    fg_color=BG_COLOR,
    scrollbar_button_color=PRIMARY,
    scrollbar_button_hover_color=PRIMARY_HOVER
)

main_scroll.pack(
    fill="both",
    expand=True
)


# =========================================================
# HEADER / NAVBAR
# =========================================================

header = ctk.CTkFrame(
    main_scroll,
    height=85,
    corner_radius=0,
    fg_color=INK
)

header.pack(
    fill="x"
)

header.pack_propagate(False)

gold_rule(main_scroll, 3).pack(fill="x")


# =========================================================
# LOGO
# =========================================================

logo_frame = ctk.CTkFrame(
    header,
    fg_color="transparent"
)

logo_frame.pack(
    side="left",
    padx=35
)


ctk.CTkLabel(
    logo_frame,
    text="AI SMART",
    font=(FONT_HEAD, 24, "bold"),
    text_color=WHITE
).pack(
    side="left"
)

ctk.CTkLabel(
    logo_frame,
    text=" ATTENDANCE",
    font=(FONT_HEAD, 24, "bold"),
    text_color=GOLD_LIGHT
).pack(
    side="left"
)


# =========================================================
# NAVIGATION
# =========================================================

nav_frame = ctk.CTkFrame(
    header,
    fg_color="transparent"
)

nav_frame.pack(
    side="right",
    padx=25
)


def nav_button(
    text,
    command
):

    return ctk.CTkButton(
        nav_frame,
        text=text,
        width=85,
        height=35,
        corner_radius=8,
        fg_color="transparent",
        hover_color="#24365C",
        text_color=WHITE,
        font=(FONT_BODY, 12, "bold"),
        command=command
    )


nav_button(
    "Home",
    lambda: scroll_to_top()
).pack(
    side="left",
    padx=3
)


nav_button(
    "About",
    lambda: about_section()
).pack(
    side="left",
    padx=3
)


nav_button(
    "Features",
    lambda: features_section()
).pack(
    side="left",
    padx=3
)


nav_button(
    "How It Works",
    lambda: process_section()
).pack(
    side="left",
    padx=3
)


nav_button(
    "Exit",
    exit_application
).pack(
    side="left",
    padx=3
)


# =========================================================
# HERO SECTION
# =========================================================

HERO_BG = "#0F1932"

hero = ctk.CTkFrame(
    main_scroll,
    fg_color=HERO_BG,
    corner_radius=28,
    border_width=1,
    border_color=GOLD
)

hero.pack(
    fill="x",
    padx=35,
    pady=30
)


hero_left = ctk.CTkFrame(
    hero,
    fg_color="transparent"
)

hero_left.pack(
    side="left",
    fill="both",
    expand=True,
    padx=45,
    pady=45
)


# Badge

ctk.CTkLabel(
    hero_left,
    text="●  AI POWERED ATTENDANCE SYSTEM",
    font=(FONT_BODY, 12, "bold"),
    text_color=GOLD_LIGHT,
    fg_color="#1E2C52",
    corner_radius=15,
    padx=15,
    pady=7
).pack(
    anchor="w"
)


# Heading

ctk.CTkLabel(
    hero_left,
    text="Smart Attendance",
    font=(FONT_HEAD, 42, "bold"),
    text_color=WHITE,
    justify="left"
).pack(
    anchor="w",
    pady=(20, 0)
)

ctk.CTkLabel(
    hero_left,
    text="Made Simple.",
    font=(FONT_HEAD, 42, "bold", "italic"),
    text_color=GOLD_LIGHT,
    justify="left"
).pack(
    anchor="w",
    pady=(0, 12)
)


# Description

ctk.CTkLabel(
    hero_left,
    text=(
        "An AI-based attendance management system "
        "that uses face recognition to identify students "
        "and automatically record attendance."
    ),
    font=(FONT_BODY, 15),
    text_color="#B4BCD3",
    justify="left",
    wraplength=550
).pack(
    anchor="w",
    pady=(0, 25)
)


# Buttons

hero_buttons = ctk.CTkFrame(
    hero_left,
    fg_color="transparent"
)

hero_buttons.pack(
    anchor="w"
)


ctk.CTkButton(
    hero_buttons,
    text="📸  Register Student",
    width=200,
    height=50,
    corner_radius=25,
    fg_color=GOLD,
    hover_color=GOLD_LIGHT,
    text_color=INK,
    font=(FONT_BODY, 13, "bold"),
    command=open_registration
).pack(
    side="left",
    padx=(0, 10)
)


ctk.CTkButton(
    hero_buttons,
    text="🔐  Login",
    width=150,
    height=50,
    corner_radius=25,
    fg_color="transparent",
    border_width=1,
    border_color=GOLD,
    hover_color="#1E2C52",
    text_color=GOLD_LIGHT,
    font=(FONT_BODY, 13, "bold"),
    command=open_login
).pack(
    side="left"
)


# =========================================================
# HERO RIGHT VISUAL
# =========================================================

hero_right = ctk.CTkFrame(
    hero,
    width=350,
    height=320,
    corner_radius=25,
    fg_color=HERO_BG,
    border_width=1,
    border_color="#33415F"
)

hero_right.pack(
    side="right",
    padx=40,
    pady=40
)

hero_right.pack_propagate(False)

ScannerCanvas(
    hero_right,
    width=316,
    height=286,
    bg=HERO_BG
).pack(
    padx=17,
    pady=17
)


# =========================================================
# PROJECT OVERVIEW
# =========================================================

overview_title = ctk.CTkLabel(
    main_scroll,
    text="About Smart Attendance System",
    font=(FONT_HEAD, 28, "bold"),
    text_color=INK
)

overview_title.pack(
    pady=(15, 5)
)


overview_subtitle = ctk.CTkLabel(
    main_scroll,
    text=(
        "A complete solution for student registration, "
        "face recognition and automatic attendance."
    ),
    font=(FONT_BODY, 13),
    text_color=MUTED_TEXT
)

overview_subtitle.pack(
    pady=(0, 20)
)


overview_card = ctk.CTkFrame(
    main_scroll,
    fg_color=WHITE,
    corner_radius=20,
    border_width=2,
    border_color=BORDER_COLOR
)

overview_card.pack(
    fill="x",
    padx=70,
    pady=10
)


ctk.CTkLabel(
    overview_card,
    text=(
        "The AI Smart Attendance System is designed to "
        "reduce manual attendance work and provide a faster "
        "and more reliable way to record student attendance.\n\n"

        "Students are first registered with their personal "
        "information and face photograph. The captured photo "
        "is stored securely with the student's registration "
        "details. During an attendance session, the system "
        "can use face recognition to identify registered "
        "students and record their attendance automatically.\n\n"

        "The system can help educational institutions reduce "
        "paperwork, save classroom time and maintain digital "
        "attendance records."
    ),
    font=(FONT_BODY, 14),
    text_color=TEXT_COLOR,
    justify="left",
    wraplength=950
).pack(
    padx=35,
    pady=30
)


# =========================================================
# FEATURES SECTION
# =========================================================

features_heading = ctk.CTkLabel(
    main_scroll,
    text="System Features",
    font=(FONT_HEAD, 28, "bold"),
    text_color=INK
)

features_heading.pack(
    pady=(35, 5)
)


ctk.CTkLabel(
    main_scroll,
    text="Everything needed for a modern attendance system",
    font=(FONT_BODY, 13),
    text_color=MUTED_TEXT
).pack(
    pady=(0, 20)
)


features_container = ctk.CTkFrame(
    main_scroll,
    fg_color="transparent"
)

features_container.pack(
    fill="x",
    padx=55
)


# =========================================================
# FEATURE CARD FUNCTION
# =========================================================

def create_feature_card(
    parent,
    icon,
    title,
    description,
    color
):

    card = ctk.CTkFrame(
        parent,
        width=245,
        height=190,
        fg_color=WHITE,
        corner_radius=18,
        border_width=2,
        border_color=BORDER_COLOR
    )

    card.pack(
        side="left",
        expand=True,
        fill="both",
        padx=8,
        pady=8
    )

    card.pack_propagate(False)

    ctk.CTkLabel(
        card,
        text=icon,
        font=(FONT_HEAD, 35),
        text_color=color
    ).pack(
        pady=(20, 8)
    )

    ctk.CTkLabel(
        card,
        text=title,
        font=(FONT_BODY, 15, "bold"),
        text_color=INK
    ).pack()

    ctk.CTkLabel(
        card,
        text=description,
        font=(FONT_BODY, 11),
        text_color=MUTED_TEXT,
        justify="center",
        wraplength=205
    ).pack(
        padx=15,
        pady=10
    )

    return card


create_feature_card(
    features_container,
    "👨‍🎓",
    "Student Registration",
    "Register student ID, PRN, name, department, class, division, email, mobile and photo.",
    PRIMARY
)


create_feature_card(
    features_container,
    "📸",
    "Face Capture",
    "Capture a clear front-facing student photograph using the camera.",
    BLUE
)


create_feature_card(
    features_container,
    "🤖",
    "Face Recognition",
    "Recognize registered students using AI-based face recognition technology.",
    GREEN
)


create_feature_card(
    features_container,
    "✅",
    "Automatic Attendance",
    "Record attendance automatically when a registered student is recognized.",
    ORANGE
)


# =========================================================
# SECOND FEATURE ROW
# =========================================================

features_container2 = ctk.CTkFrame(
    main_scroll,
    fg_color="transparent"
)

features_container2.pack(
    fill="x",
    padx=55,
    pady=(0, 20)
)


create_feature_card(
    features_container2,
    "💾",
    "Digital Records",
    "Store student registration and attendance information digitally.",
    PRIMARY
)


create_feature_card(
    features_container2,
    "📊",
    "Attendance Records",
    "Maintain organized attendance information for registered students.",
    BLUE
)


create_feature_card(
    features_container2,
    "📈",
    "Reports",
    "Attendance information can be used to generate useful reports.",
    GREEN
)


create_feature_card(
    features_container2,
    "🔒",
    "Secure Data",
    "Student details and captured photographs are stored locally within the project.",
    ORANGE
)


# =========================================================
# HOW IT WORKS
# =========================================================

process_heading = ctk.CTkLabel(
    main_scroll,
    text="How The System Works",
    font=(FONT_HEAD, 28, "bold"),
    text_color=INK
)

process_heading.pack(
    pady=(35, 5)
)


ctk.CTkLabel(
    main_scroll,
    text="Simple workflow from student registration to attendance",
    font=(FONT_BODY, 13),
    text_color=MUTED_TEXT
).pack(
    pady=(0, 20)
)


process_frame = ctk.CTkFrame(
    main_scroll,
    fg_color=WHITE,
    corner_radius=20,
    border_width=2,
    border_color=BORDER_COLOR
)

process_frame.pack(
    fill="x",
    padx=60,
    pady=10
)


process_data = [

    (
        "01",
        "Student Registration",
        "Enter student information and create a student record.",
        PRIMARY
    ),

    (
        "02",
        "Face Capture",
        "Capture a clear photograph of the student's face.",
        BLUE
    ),

    (
        "03",
        "Face Enrollment",
        "Store the captured image together with student details.",
        GREEN
    ),

    (
        "04",
        "Attendance Session",
        "Start the attendance process for a class or session.",
        ORANGE
    ),

    (
        "05",
        "Face Recognition",
        "Identify students using their registered face data.",
        PRIMARY
    ),

    (
        "06",
        "Attendance Record",
        "Save attendance information for future records and reports.",
        BLUE
    )
]


for number, title, description, color in process_data:

    row = ctk.CTkFrame(
        process_frame,
        fg_color="transparent"
    )

    row.pack(
        fill="x",
        padx=30,
        pady=12
    )

    number_label = ctk.CTkLabel(
        row,
        text=number,
        width=55,
        height=55,
        corner_radius=28,
        fg_color=color,
        text_color=WHITE,
        font=(FONT_BODY, 15, "bold")
    )

    number_label.pack(
        side="left"
    )

    text_frame = ctk.CTkFrame(
        row,
        fg_color="transparent"
    )

    text_frame.pack(
        side="left",
        padx=20
    )

    ctk.CTkLabel(
        text_frame,
        text=title,
        font=(FONT_BODY, 15, "bold"),
        text_color=INK
    ).pack(
        anchor="w"
    )

    ctk.CTkLabel(
        text_frame,
        text=description,
        font=(FONT_BODY, 11),
        text_color=MUTED_TEXT
    ).pack(
        anchor="w",
        pady=3
    )


# =========================================================
# TECHNOLOGY SECTION
# =========================================================

tech_heading = ctk.CTkLabel(
    main_scroll,
    text="Technology Used",
    font=(FONT_HEAD, 28, "bold"),
    text_color=INK
)

tech_heading.pack(
    pady=(35, 20)
)


tech_frame = ctk.CTkFrame(
    main_scroll,
    fg_color="transparent"
)

tech_frame.pack(
    fill="x",
    padx=100
)


technologies = [

    ("🐍", "Python", "Main programming language"),

    ("👁", "OpenCV", "Camera and image processing"),

    ("🎨", "CustomTkinter", "Modern desktop interface"),

    ("🖼", "Pillow", "Image processing"),

    ("📄", "JSON", "Student data storage")
]


for icon, title, description in technologies:

    card = ctk.CTkFrame(
        tech_frame,
        width=190,
        height=135,
        fg_color=WHITE,
        corner_radius=15,
        border_width=1,
        border_color=BORDER_COLOR
    )

    card.pack(
        side="left",
        expand=True,
        fill="both",
        padx=6
    )

    card.pack_propagate(False)

    ctk.CTkLabel(
        card,
        text=icon,
        font=(FONT_HEAD, 28)
    ).pack(
        pady=(15, 5)
    )

    ctk.CTkLabel(
        card,
        text=title,
        font=(FONT_BODY, 14, "bold"),
        text_color=INK
    ).pack()

    ctk.CTkLabel(
        card,
        text=description,
        font=(FONT_BODY, 10),
        text_color=MUTED_TEXT
    ).pack(
        pady=5
    )


# =========================================================
# START REGISTRATION SECTION
# =========================================================

start_card = ctk.CTkFrame(
    main_scroll,
    fg_color=INK,
    corner_radius=25
)

start_card.pack(
    fill="x",
    padx=60,
    pady=45
)


ctk.CTkLabel(
    start_card,
    text="Ready to Register a Student?",
    font=(FONT_HEAD, 28, "bold"),
    text_color=WHITE
).pack(
    pady=(30, 8)
)


ctk.CTkLabel(
    start_card,
    text=(
        "Start student registration and capture the student's "
        "face photograph."
    ),
    font=(FONT_BODY, 13),
    text_color="#D9C28F"
).pack(
    pady=(0, 20)
)


ctk.CTkButton(
    start_card,
    text="📸  START STUDENT REGISTRATION",
    width=280,
    height=50,
    corner_radius=12,
    fg_color=PRIMARY,
    hover_color=PRIMARY_HOVER,
    text_color=WHITE,
    font=(FONT_BODY, 13, "bold"),
    command=open_registration
).pack(
    pady=(0, 30)
)


# =========================================================
# FOOTER
# =========================================================

footer = ctk.CTkFrame(
    main_scroll,
    height=110,
    fg_color=INK,
    corner_radius=0
)

footer.pack(
    fill="x"
)

footer.pack_propagate(False)


ctk.CTkLabel(
    footer,
    text="AI SMART ATTENDANCE SYSTEM",
    font=(FONT_BODY, 16, "bold"),
    text_color=WHITE
).pack(
    pady=(20, 5)
)


ctk.CTkLabel(
    footer,
    text="Smart • Automated • AI Powered Attendance",
    font=(FONT_BODY, 11),
    text_color="#DDD2BD"
).pack()


ctk.CTkLabel(
    footer,
    text="© 2026 Smart Attendance System",
    font=(FONT_BODY, 10),
    text_color="#D9C28F"
).pack(
    pady=5
)


# =========================================================
# NAVIGATION FUNCTIONS
# =========================================================

def scroll_to_top():

    try:
        main_scroll._parent_canvas.yview_moveto(0)
    except:
        pass


def about_section():

    try:
        main_scroll._parent_canvas.yview_moveto(0.22)
    except:
        pass


def features_section():

    try:
        main_scroll._parent_canvas.yview_moveto(0.40)
    except:
        pass


def process_section():

    try:
        main_scroll._parent_canvas.yview_moveto(0.62)
    except:
        pass


# =========================================================
# START APPLICATION
# =========================================================

print("HOME.PY IS RUNNING")

app.mainloop()