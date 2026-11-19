"""
Interface pieces for concurrent attendance sessions:

* identify_faculty()   - who is taking attendance in this window
* SessionBar           - live status strip (my session + other faculty's sessions)
* StartSessionDialog   - pick class / division / students and go live
* RosterWindow         - who is present / pending in my session

Business rules live in session_store.py; this module only presents them.
"""

import hashlib
import json
import os
from datetime import datetime
from tkinter import messagebox, ttk

import customtkinter as ctk

import session_store as ss
from theme import (
    fit_geometry, maximize,
    BG_COLOR, BORDER_COLOR, DANGER, FONT_BODY, FONT_HEAD, GOLD, GOLD_DEEP,
    GOLD_LIGHT, GREY_HOVER, INK, LIGHT_AMBER, LIGHT_GREY, LIGHT_RED, MUTED_TEXT,
    PRIMARY, PRIMARY_HOVER, SUCCESS, TEXT_COLOR, TINT, WARNING, WHITE,
    GradientLine,
)

USER_FILE = os.path.join(ss.BASE_DIR, "users.json")
ALLOWED_ROLES = ("Faculty", "Admin")
LIVE_GREEN = "#2F6B4F"
LIVE_GREEN_SOFT = "#8CC9A7"


# =========================================================
# FACULTY IDENTITY
# =========================================================

def _load_users():
    try:
        with open(USER_FILE, "r", encoding="utf-8") as handle:
            data = json.load(handle)
        return data if isinstance(data, list) else []
    except (OSError, json.JSONDecodeError):
        return []


def user_from_environment():
    """Identity handed over by login.py when this window was launched."""
    user_id = os.environ.get("SMARTMARK_USER_ID", "").strip()
    if not user_id:
        return None
    return {
        "user_id": user_id,
        "full_name": os.environ.get("SMARTMARK_USER_NAME", user_id),
        "role": os.environ.get("SMARTMARK_USER_ROLE", ""),
        "department": os.environ.get("SMARTMARK_USER_DEPT", ""),
    }


class _SignIn(ctk.CTkToplevel):

    def __init__(self, parent):
        super().__init__(parent, fg_color=BG_COLOR)
        self.user = None
        self.attempts = 0
        self.title("Faculty Sign-in")
        self.resizable(False, False)
        fit_geometry(self, 430, 470)

        top = ctk.CTkFrame(self, fg_color=INK, corner_radius=0, height=108)
        top.pack(fill="x")
        top.pack_propagate(False)
        ctk.CTkLabel(top, text="FACULTY SIGN-IN", font=(FONT_BODY, 11, "bold"),
                     text_color=GOLD_LIGHT).pack(anchor="w", padx=30, pady=(22, 0))
        ctk.CTkLabel(top, text="Take Attendance", font=(FONT_HEAD, 25, "bold"),
                     text_color=WHITE).pack(anchor="w", padx=30)
        GradientLine(self, height=3, bg=BG_COLOR).pack(fill="x")

        ctk.CTkLabel(self, text="Sign in so your class session is recorded under your name.",
                     font=(FONT_BODY, 11), text_color=MUTED_TEXT, wraplength=360,
                     justify="left").pack(anchor="w", padx=30, pady=(18, 10))

        self.email = ctk.CTkEntry(self, width=370, height=42, corner_radius=12,
                                  placeholder_text="Faculty email", fg_color=WHITE,
                                  border_color=BORDER_COLOR, border_width=2,
                                  text_color=TEXT_COLOR)
        self.email.pack(pady=5)
        self.password = ctk.CTkEntry(self, width=370, height=42, corner_radius=12,
                                     placeholder_text="Password", show="•",
                                     fg_color=WHITE, border_color=BORDER_COLOR,
                                     border_width=2, text_color=TEXT_COLOR)
        self.password.pack(pady=5)
        self.error = ctk.CTkLabel(self, text="", font=(FONT_BODY, 11), text_color=DANGER,
                                  wraplength=360)
        self.error.pack(pady=(4, 0))
        ctk.CTkButton(self, text="Sign in", width=370, height=46, corner_radius=23,
                      fg_color=GOLD, hover_color=GOLD_LIGHT, text_color=INK,
                      font=(FONT_BODY, 14, "bold"), command=self._submit).pack(pady=(12, 6))
        ctk.CTkButton(self, text="Cancel", width=370, height=36, corner_radius=18,
                      fg_color="transparent", text_color=MUTED_TEXT,
                      hover_color=LIGHT_GREY, command=self._close).pack()
        self.bind("<Return>", lambda e: self._submit())
        self.protocol("WM_DELETE_WINDOW", self._close)
        self.after(150, self._focus)

    def _focus(self):
        try:
            self.lift()
            self.focus_force()
            self.grab_set()
            self.email.focus()
        except Exception:
            pass

    def _submit(self):
        email = self.email.get().strip().lower()
        digest = hashlib.sha256(self.password.get().encode("utf-8")).hexdigest()
        for user in _load_users():
            if str(user.get("email", "")).strip().lower() == email and user.get("password") == digest:
                if user.get("role") not in ALLOWED_ROLES:
                    self.error.configure(text="Only Faculty or Admin accounts can take attendance.")
                    return
                self.user = {
                    "user_id": user.get("user_id", email),
                    "full_name": user.get("full_name", email),
                    "role": user.get("role", ""),
                    "department": user.get("department", ""),
                }
                self.destroy()
                return
        self.attempts += 1
        self.error.configure(text="Invalid email or password.")
        if self.attempts >= 5:
            self._close()

    def _close(self):
        self.user = None
        self.destroy()


def identify_faculty(root):
    """Return the signed-in faculty dict, or None if they cancelled / are not allowed."""
    user = user_from_environment()
    if user:
        if user["role"] not in ALLOWED_ROLES:
            messagebox.showerror(
                "Access Restricted",
                "Only Faculty or Admin accounts can take attendance.")
            return None
        return user
    dialog = _SignIn(root)
    root.wait_window(dialog)
    return dialog.user


# =========================================================
# SESSION BAR
# =========================================================

class SessionBar(ctk.CTkFrame):
    """Top strip: my live session, and who else is live right now."""

    def __init__(self, parent, user, on_start, on_end, on_roster):
        super().__init__(parent, fg_color=WHITE, corner_radius=16,
                         border_width=1, border_color=BORDER_COLOR)
        self.user = user
        self.session = None
        self.marked = 0
        self._pulse_on = True

        left = ctk.CTkFrame(self, fg_color="transparent")
        left.pack(side="left", padx=(20, 10), pady=12)
        row = ctk.CTkFrame(left, fg_color="transparent")
        row.pack(anchor="w")
        self.dot = ctk.CTkLabel(row, text="●", font=(FONT_BODY, 16), text_color=MUTED_TEXT)
        self.dot.pack(side="left", padx=(0, 8))
        self.title = ctk.CTkLabel(row, text="No active session", font=(FONT_HEAD, 17, "bold"),
                                  text_color=INK)
        self.title.pack(side="left")
        self.detail = ctk.CTkLabel(left, text="", anchor="w", font=(FONT_BODY, 11),
                                   text_color=MUTED_TEXT)
        self.detail.pack(anchor="w", pady=(2, 0))

        right = ctk.CTkFrame(self, fg_color="transparent")
        right.pack(side="right", padx=(10, 18), pady=12)
        self.roster_btn = ctk.CTkButton(
            right, text="👥  Roster", width=104, height=38, corner_radius=19,
            fg_color=TINT, hover_color=GREY_HOVER, text_color=INK,
            font=(FONT_BODY, 12, "bold"), command=on_roster)
        self.end_btn = ctk.CTkButton(
            right, text="■  End Session", width=140, height=38, corner_radius=19,
            fg_color="transparent", border_width=1, border_color=DANGER,
            hover_color=LIGHT_RED, text_color=DANGER,
            font=(FONT_BODY, 12, "bold"), command=on_end)
        self.start_btn = ctk.CTkButton(
            right, text="▶  Start Session", width=160, height=38, corner_radius=19,
            fg_color=GOLD, hover_color=GOLD_LIGHT, text_color=INK,
            font=(FONT_BODY, 12, "bold"), command=on_start)

        self.others = ctk.CTkFrame(self, fg_color="transparent")
        self.others.pack(side="left", fill="x", expand=True, padx=10)

        self.set_session(None)
        self._pulse()

    # ---- state ------------------------------------------------------
    def set_session(self, session, marked=0):
        self.session = session
        self.marked = marked
        for button in (self.roster_btn, self.end_btn, self.start_btn):
            button.pack_forget()
        if session:
            self.end_btn.pack(side="right", padx=(8, 0))
            self.roster_btn.pack(side="right")
            self.title.configure(
                text=f"{session['subject']}  ·  {session['class']}-{session['division']}")
            self.dot.configure(text_color=LIVE_GREEN)
            self._update_detail()
        else:
            self.start_btn.pack(side="right")
            self.title.configure(text="No active session")
            self.dot.configure(text_color=MUTED_TEXT)
            self.detail.configure(text="Start a session to begin marking attendance")

    def set_marked(self, count):
        self.marked = count
        self._update_detail()

    def _update_detail(self):
        if not self.session:
            return
        total = len(self.session["student_ids"])
        started = self.session["started_at"][11:16]
        self.detail.configure(
            text=f"LIVE  ·  {self.marked} of {total} marked  ·  started {started}")

    def refresh_others(self):
        """Redraw the chips for other faculty's live sessions."""
        mine = self.session["session_id"] if self.session else None
        others = [s for s in ss.live_sessions() if s["session_id"] != mine]
        for child in self.others.winfo_children():
            child.destroy()
        if not others:
            ctk.CTkLabel(self.others, text="No other faculty are live right now",
                         font=(FONT_BODY, 11), text_color=MUTED_TEXT).pack(side="left", padx=8)
            return
        ctk.CTkLabel(self.others, text="LIVE NOW", font=(FONT_BODY, 10, "bold"),
                     text_color=GOLD_DEEP).pack(side="left", padx=(8, 8))
        for session in others[:3]:
            chip = ctk.CTkLabel(
                self.others, fg_color=TINT, text_color=INK, corner_radius=12,
                font=(FONT_BODY, 11, "bold"), padx=12, pady=5,
                text=(f"●  {session['faculty_name']}  ·  {session['subject']}  ·  "
                      f"{session['class']}-{session['division']}  ·  "
                      f"{len(session['student_ids'])}"))
            chip.pack(side="left", padx=3)
        if len(others) > 3:
            ctk.CTkLabel(self.others, text=f"+{len(others) - 3} more",
                         font=(FONT_BODY, 11, "bold"), text_color=MUTED_TEXT).pack(side="left", padx=6)

    def _pulse(self):
        if self.session:
            self.dot.configure(text_color=LIVE_GREEN if self._pulse_on else LIVE_GREEN_SOFT)
            self._pulse_on = not self._pulse_on
        try:
            self.after(650, self._pulse)
        except Exception:
            pass


# =========================================================
# START SESSION
# =========================================================

class StartSessionDialog(ctk.CTkToplevel):
    """Choose class/division/students and go live. `.session` holds the result."""

    def __init__(self, parent, students, user):
        super().__init__(parent, fg_color=BG_COLOR)
        self.students = students
        self.user = user
        self.session = None
        self.selected = set()
        self._busy_snapshot = None
        self._seeded = set()

        self.title("Start Attendance Session")
        self.resizable(False, False)
        fit_geometry(self, 700, 720)

        top = ctk.CTkFrame(self, fg_color=INK, corner_radius=0, height=92)
        top.pack(fill="x")
        top.pack_propagate(False)
        ctk.CTkLabel(top, text="NEW SESSION", font=(FONT_BODY, 11, "bold"),
                     text_color=GOLD_LIGHT).pack(anchor="w", padx=30, pady=(18, 0))
        ctk.CTkLabel(top, text="Start Attendance Session", font=(FONT_HEAD, 24, "bold"),
                     text_color=WHITE).pack(anchor="w", padx=30)
        GradientLine(self, height=3, bg=BG_COLOR).pack(fill="x")

        form = ctk.CTkFrame(self, fg_color="transparent")
        form.pack(fill="x", padx=28, pady=(16, 4))
        self.subject = ctk.CTkEntry(form, width=300, height=40, corner_radius=12,
                                    placeholder_text="Subject / lecture *", fg_color=WHITE,
                                    border_color=BORDER_COLOR, border_width=2,
                                    text_color=TEXT_COLOR)
        self.subject.pack(side="left")

        classes = sorted({str(s.get("class", "")).strip() for s in students if s.get("class")})
        divisions = sorted({str(s.get("division", "")).strip() for s in students if s.get("division")})
        self.class_box = ctk.CTkComboBox(
            form, width=140, height=40, corner_radius=12, values=["All classes"] + classes,
            fg_color=WHITE, border_color=BORDER_COLOR, button_color=INK,
            button_hover_color=PRIMARY_HOVER, text_color=TEXT_COLOR,
            dropdown_fg_color=WHITE, dropdown_hover_color=TINT, dropdown_text_color=TEXT_COLOR,
            command=lambda _v: self._reseed(), state="readonly")
        self.class_box.set("All classes")
        self.class_box.pack(side="left", padx=(10, 0))
        self.div_box = ctk.CTkComboBox(
            form, width=140, height=40, corner_radius=12, values=["All divisions"] + divisions,
            fg_color=WHITE, border_color=BORDER_COLOR, button_color=INK,
            button_hover_color=PRIMARY_HOVER, text_color=TEXT_COLOR,
            dropdown_fg_color=WHITE, dropdown_hover_color=TINT, dropdown_text_color=TEXT_COLOR,
            command=lambda _v: self._reseed(), state="readonly")
        self.div_box.set("All divisions")
        self.div_box.pack(side="left", padx=(10, 0))

        rule = ctk.CTkFrame(self, fg_color=LIGHT_AMBER, corner_radius=12,
                            border_width=1, border_color=GOLD)
        rule.pack(fill="x", padx=28, pady=(10, 6))
        ctk.CTkLabel(
            rule, anchor="w", justify="left", wraplength=610, font=(FONT_BODY, 11),
            text_color=TEXT_COLOR,
            text=("A student can be in only one live session at a time. Students already "
                  "taken by another faculty are locked until that session ends. "
                  "Untick anyone who is not in your class."),
        ).pack(fill="x", padx=14, pady=9)

        bar = ctk.CTkFrame(self, fg_color="transparent")
        bar.pack(fill="x", padx=28)
        self.counter = ctk.CTkLabel(bar, text="", font=(FONT_BODY, 12, "bold"), text_color=INK)
        self.counter.pack(side="left")
        for text, command in (("Clear", self._clear), ("Select all available", self._select_all)):
            ctk.CTkButton(bar, text=text, width=140 if "all" in text else 70, height=30,
                          corner_radius=15, fg_color=TINT, hover_color=GREY_HOVER,
                          text_color=INK, font=(FONT_BODY, 11, "bold"),
                          command=command).pack(side="right", padx=(6, 0))

        self.list = ctk.CTkScrollableFrame(
            self, fg_color=WHITE, corner_radius=14, border_width=1, border_color=BORDER_COLOR,
            scrollbar_button_color=GOLD, scrollbar_button_hover_color=GOLD_DEEP, height=330)
        self.list.pack(fill="both", expand=True, padx=28, pady=(8, 6))

        self.message = ctk.CTkLabel(self, text="", font=(FONT_BODY, 11, "bold"),
                                    text_color=DANGER, wraplength=620, justify="left")
        self.message.pack(anchor="w", padx=30)

        buttons = ctk.CTkFrame(self, fg_color="transparent")
        buttons.pack(fill="x", padx=28, pady=(6, 16))
        ctk.CTkButton(buttons, text="Cancel", width=120, height=44, corner_radius=22,
                      fg_color="transparent", border_width=1, border_color=BORDER_COLOR,
                      text_color=MUTED_TEXT, hover_color=LIGHT_GREY,
                      font=(FONT_BODY, 13, "bold"), command=self.destroy).pack(side="right", padx=(10, 0))
        self.go_btn = ctk.CTkButton(buttons, text="Go Live", width=190, height=44, corner_radius=22,
                                    fg_color=GOLD, hover_color=GOLD_LIGHT, text_color=INK,
                                    font=(FONT_BODY, 13, "bold"), command=self._start)
        self.go_btn.pack(side="right")

        self._reseed()
        self._poll()
        self.after(150, self._focus)

    def _focus(self):
        try:
            self.lift()
            self.focus_force()
            self.grab_set()
            self.subject.focus()
        except Exception:
            pass

    # ---- roster list --------------------------------------------------
    def _matching(self):
        cls, div = self.class_box.get(), self.div_box.get()
        out = []
        for student in self.students:
            if cls != "All classes" and str(student.get("class", "")).strip() != cls:
                continue
            if div != "All divisions" and str(student.get("division", "")).strip() != div:
                continue
            out.append(student)
        return out

    def _reseed(self):
        """Class/division changed: pre-select everyone available in that group."""
        busy = ss.busy_students()
        self.selected = {str(s.get("student_id")) for s in self._matching()
                         if str(s.get("student_id")) not in busy}
        self._busy_snapshot = None
        self._render(busy)

    def _render(self, busy=None):
        busy = ss.busy_students() if busy is None else busy
        self._busy_snapshot = {k: v["session_id"] for k, v in busy.items()}
        for child in self.list.winfo_children():
            child.destroy()
        matching = self._matching()
        locked = 0
        for student in matching:
            sid = str(student.get("student_id"))
            row = ctk.CTkFrame(self.list, fg_color="transparent")
            row.pack(fill="x", padx=6, pady=1)
            if sid in busy:
                locked += 1
                self.selected.discard(sid)
                holder = busy[sid]
                box = ctk.CTkCheckBox(row, text=f"{student.get('name', '')}  ({sid})", state="disabled",
                                      font=(FONT_BODY, 12), text_color_disabled=MUTED_TEXT,
                                      fg_color=INK, border_color=BORDER_COLOR)
                box.pack(side="left", pady=3)
                ctk.CTkLabel(
                    row, text=f"🔒 {holder['faculty_name']} · {holder['subject']}",
                    font=(FONT_BODY, 10, "bold"), text_color=WARNING, fg_color=LIGHT_AMBER,
                    corner_radius=9, padx=9, pady=2).pack(side="right")
            else:
                var = ctk.BooleanVar(value=sid in self.selected)
                ctk.CTkCheckBox(
                    row, text=f"{student.get('name', '')}  ({sid})", variable=var,
                    font=(FONT_BODY, 12), text_color=TEXT_COLOR, fg_color=INK,
                    hover_color=PRIMARY_HOVER, border_color=GOLD_DEEP, checkmark_color=GOLD_LIGHT,
                    command=lambda s=sid, v=var: self._toggle(s, v)).pack(side="left", pady=3)
        if not matching:
            ctk.CTkLabel(self.list, text="No registered students in this class / division.",
                         font=(FONT_BODY, 12), text_color=MUTED_TEXT).pack(pady=40)
        self._counter(len(matching), locked)

    def _counter(self, total=None, locked=None):
        total = len(self._matching()) if total is None else total
        self.counter.configure(
            text=f"{len(self.selected)} selected   ·   {total} in group"
                 + (f"   ·   {locked} locked" if locked else ""))

    def _toggle(self, sid, var):
        (self.selected.add if var.get() else self.selected.discard)(sid)
        self._counter()

    def _select_all(self):
        busy = ss.busy_students()
        self.selected = {str(s.get("student_id")) for s in self._matching()
                         if str(s.get("student_id")) not in busy}
        self._render(busy)

    def _clear(self):
        self.selected.clear()
        self._render()

    def _poll(self):
        """Pick up other faculty starting/ending sessions while this dialog is open."""
        try:
            busy = ss.busy_students()
            snapshot = {k: v["session_id"] for k, v in busy.items()}
            if snapshot != self._busy_snapshot:
                self._render(busy)
            self.after(3000, self._poll)
        except Exception:
            pass

    # ---- go live ------------------------------------------------------
    def _start(self):
        subject = self.subject.get().strip()
        if not subject:
            self.message.configure(text="Please enter the subject / lecture name.")
            self.subject.focus()
            return
        if not self.selected:
            self.message.configure(text="Select at least one student for this session.")
            return
        cls, div = self.class_box.get(), self.div_box.get()
        try:
            ok, info = ss.start_session(
                self.user["user_id"], self.user["full_name"], subject,
                "All" if cls == "All classes" else cls,
                "All" if div == "All divisions" else div,
                sorted(self.selected))
        except TimeoutError as error:
            self.message.configure(text=str(error))
            return

        if ok:
            self.session = info
            self.destroy()
            return

        if info["reason"] == "faculty_busy":
            self.message.configure(
                text="You already have a live session. End it before starting another.")
        elif info["reason"] == "conflict":
            names = {str(s.get("student_id")): s.get("name", "") for s in self.students}
            lines = [f"{names.get(c['student_id'], c['student_id'])} is in {c['faculty_name']}'s "
                     f"{c['subject']} session" for c in info["conflicts"][:4]]
            more = len(info["conflicts"]) - 4
            self.message.configure(
                text="Another faculty just took some of these students:\n" + "\n".join(lines)
                     + (f"\n…and {more} more." if more > 0 else ""))
            self._render()
        else:
            self.message.configure(text="Select at least one student for this session.")


# =========================================================
# ROSTER
# =========================================================

class RosterWindow(ctk.CTkToplevel):
    """Present / pending list for the faculty's own live session."""

    def __init__(self, parent, session, students, on_select):
        super().__init__(parent, fg_color=BG_COLOR)
        self.session = session
        self.on_select = on_select
        by_id = {str(s.get("student_id")): s for s in students}
        self.students = [by_id[i] for i in session["student_ids"] if i in by_id]

        self.title("Session Roster")
        fit_geometry(self, 560, 560)

        top = ctk.CTkFrame(self, fg_color=INK, corner_radius=0, height=84)
        top.pack(fill="x")
        top.pack_propagate(False)
        ctk.CTkLabel(top, text=f"{session['subject']}  ·  {session['class']}-{session['division']}",
                     font=(FONT_HEAD, 20, "bold"), text_color=WHITE).pack(anchor="w", padx=26, pady=(16, 0))
        self.summary = ctk.CTkLabel(top, text="", font=(FONT_BODY, 11), text_color=GOLD_LIGHT)
        self.summary.pack(anchor="w", padx=26)
        GradientLine(self, height=3, bg=BG_COLOR).pack(fill="x")

        style = ttk.Style()
        style.configure("Roster.Treeview", rowheight=30, font=(FONT_BODY, 10),
                        background=WHITE, fieldbackground=WHITE, foreground=TEXT_COLOR)
        style.configure("Roster.Treeview.Heading", font=(FONT_BODY, 10, "bold"),
                        background=INK, foreground=WHITE)
        frame = ctk.CTkFrame(self, fg_color=WHITE, corner_radius=12)
        frame.pack(fill="both", expand=True, padx=20, pady=(14, 8))
        self.tree = ttk.Treeview(frame, columns=("id", "name", "status"), show="headings",
                                 style="Roster.Treeview")
        for key, text, width in (("id", "ID", 90), ("name", "Name", 280), ("status", "Status", 110)):
            self.tree.heading(key, text=text)
            self.tree.column(key, width=width, anchor="w" if key != "status" else "center")
        self.tree.tag_configure("present", foreground=SUCCESS)
        self.tree.tag_configure("pending", foreground=MUTED_TEXT)
        self.tree.pack(fill="both", expand=True, padx=6, pady=6)
        self.tree.bind("<Double-1>", lambda e: self._select())

        row = ctk.CTkFrame(self, fg_color="transparent")
        row.pack(fill="x", padx=20, pady=(0, 14))
        ctk.CTkLabel(row, text="Double-click a student to select them for marking.",
                     font=(FONT_BODY, 11), text_color=MUTED_TEXT).pack(side="left")
        ctk.CTkButton(row, text="Select", width=100, height=36, corner_radius=18,
                      fg_color=GOLD, hover_color=GOLD_LIGHT, text_color=INK,
                      font=(FONT_BODY, 12, "bold"), command=self._select).pack(side="right")
        self.refresh()

    def refresh(self):
        present = {str(r.get("student_id")) for r in ss.session_attendance(self.session["session_id"])}
        for item in self.tree.get_children():
            self.tree.delete(item)
        for student in self.students:
            sid = str(student.get("student_id"))
            here = sid in present
            self.tree.insert("", "end", iid=sid, tags=("present" if here else "pending",),
                             values=(sid, student.get("name", ""), "✓ Present" if here else "Pending"))
        self.summary.configure(
            text=f"{len(present)} present  ·  {len(self.students) - len(present)} pending")

    def _select(self):
        chosen = self.tree.selection()
        if not chosen:
            return
        student = next((s for s in self.students if str(s.get("student_id")) == chosen[0]), None)
        if student:
            self.on_select(student)
            self.destroy()
