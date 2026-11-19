"""
Live attendance sessions shared by several faculty at the same time.

Rules enforced here (not in the UI), so they hold even when two faculty
press the button in the same instant from two different windows:

* A *session* is one faculty member taking attendance for one roster of
  students (a class/division, or any subset of it).
* Any number of sessions may be live at once.
* A student can belong to only ONE live session at a time. Starting a
  session whose roster overlaps a live one is refused, and the overlapping
  students are reported with the faculty member who holds them.
* A faculty member can run only one live session at a time.
* Attendance can only be marked for a student on the roster of the marking
  faculty's own live session, and only once per session.
* A session whose window stops sending heartbeats (crash, closed laptop)
  expires automatically after STALE_AFTER seconds so students are never
  locked out for good.

All reads-modify-writes go through one cross-process file lock and files
are replaced atomically, so simultaneous writers never lose each other's
records or corrupt the JSON.
"""

import json
import os
import random
import time
import uuid
from datetime import datetime

BASE_DIR = os.environ.get("SMARTMARK_DATA_DIR") or os.path.dirname(os.path.abspath(__file__))

SESSIONS_FILE = os.path.join(BASE_DIR, "sessions.json")
ATTENDANCE_FILE = os.path.join(BASE_DIR, "attendance.json")
LOCK_FILE = os.path.join(BASE_DIR, ".smartmark.lock")

STALE_AFTER = 75          # seconds without a heartbeat before a session expires
HEARTBEAT_EVERY = 10      # seconds between heartbeats from an open dashboard


# =========================================================
# CROSS-PROCESS LOCK
# =========================================================

class FileLock:
    """Exclusive lock using an atomically-created lock file (Windows + Linux)."""

    def __init__(self, path=None, timeout=10.0, stale=20.0):
        self.path = path or LOCK_FILE
        self.timeout = timeout
        self.stale = stale

    def __enter__(self):
        start = time.time()
        while True:
            try:
                fd = os.open(self.path, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
                os.write(fd, str(os.getpid()).encode())
                os.close(fd)
                return self
            except FileExistsError:
                try:                                   # lock left behind by a crash
                    if time.time() - os.path.getmtime(self.path) > self.stale:
                        os.remove(self.path)
                        continue
                except OSError:
                    pass
                if time.time() - start > self.timeout:
                    raise TimeoutError("Could not obtain the data lock. Please try again.")
                time.sleep(random.uniform(0.005, 0.03))

    def __exit__(self, *exc):
        try:
            os.remove(self.path)
        except OSError:
            pass
        return False


# =========================================================
# JSON HELPERS
# =========================================================

def _read(path):
    for attempt in range(6):
        try:
            with open(path, "r", encoding="utf-8") as handle:
                data = json.load(handle)
            return data if isinstance(data, list) else []
        except FileNotFoundError:
            return []
        except (json.JSONDecodeError, PermissionError, OSError):
            time.sleep(0.02 * (attempt + 1))
    return []


def _write(path, data):
    tmp = f"{path}.{os.getpid()}.tmp"
    with open(tmp, "w", encoding="utf-8") as handle:
        json.dump(data, handle, indent=4, ensure_ascii=False)
        handle.flush()
        os.fsync(handle.fileno())
    for attempt in range(8):
        try:
            os.replace(tmp, path)
            return
        except PermissionError:                        # Windows: a reader has it open
            time.sleep(0.03 * (attempt + 1))
    os.replace(tmp, path)


def _stamp():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


# =========================================================
# SESSIONS
# =========================================================

def _is_live(session, now=None):
    now = now or time.time()
    return (
        session.get("status") == "active"
        and now - float(session.get("last_heartbeat", 0)) <= STALE_AFTER
    )


def _expire_stale(sessions, now):
    changed = False
    for session in sessions:
        if session.get("status") == "active" and not _is_live(session, now):
            session["status"] = "expired"
            session["ended_at"] = _stamp()
            changed = True
    return changed


def all_sessions():
    return _read(SESSIONS_FILE)


def live_sessions():
    """Every currently live session (read-only, no lock needed)."""
    now = time.time()
    return [s for s in all_sessions() if _is_live(s, now)]


def get_session(session_id):
    for session in all_sessions():
        if session.get("session_id") == session_id:
            return session
    return None


def busy_students(exclude_session_id=None):
    """{student_id: session} for students held by a live session."""
    busy = {}
    for session in live_sessions():
        if session.get("session_id") == exclude_session_id:
            continue
        for student_id in session.get("student_ids", []):
            busy[student_id] = session
    return busy


def start_session(faculty_id, faculty_name, subject, class_name, division, student_ids):
    """
    Atomically claim `student_ids` for a new live session.

    Returns (True, session) or (False, info) where info["reason"] is one of
    "empty", "faculty_busy" or "conflict" (with info["conflicts"] listing each
    contested student and who holds them).
    """
    student_ids = list(dict.fromkeys(str(s) for s in student_ids))
    if not student_ids:
        return False, {"reason": "empty"}

    with FileLock():
        sessions = all_sessions()
        now = time.time()
        if _expire_stale(sessions, now):
            _write(SESSIONS_FILE, sessions)

        live = [s for s in sessions if _is_live(s, now)]

        for session in live:
            if session.get("faculty_id") == faculty_id:
                return False, {"reason": "faculty_busy", "session": session}

        claimed = {}
        for session in live:
            for student_id in session.get("student_ids", []):
                claimed[student_id] = session
        conflicts = [
            {
                "student_id": sid,
                "faculty_name": claimed[sid].get("faculty_name", "another faculty"),
                "subject": claimed[sid].get("subject", ""),
                "class": claimed[sid].get("class", ""),
                "division": claimed[sid].get("division", ""),
            }
            for sid in student_ids if sid in claimed
        ]
        if conflicts:
            return False, {"reason": "conflict", "conflicts": conflicts}

        session = {
            "session_id": uuid.uuid4().hex[:12],
            "faculty_id": faculty_id,
            "faculty_name": faculty_name,
            "subject": subject,
            "class": class_name,
            "division": division,
            "student_ids": student_ids,
            "status": "active",
            "started_at": _stamp(),
            "ended_at": "",
            "last_heartbeat": now,
        }
        sessions.append(session)
        _write(SESSIONS_FILE, sessions)
        return True, session


def heartbeat(session_id):
    """Keep a session alive. Returns False if it has already ended/expired."""
    with FileLock():
        sessions = all_sessions()
        now = time.time()
        alive = False
        for session in sessions:
            if session.get("session_id") == session_id:
                if _is_live(session, now):
                    session["last_heartbeat"] = now
                    alive = True
                break
        _expire_stale(sessions, now)
        _write(SESSIONS_FILE, sessions)
        return alive


def end_session(session_id, status="ended"):
    with FileLock():
        sessions = all_sessions()
        for session in sessions:
            if session.get("session_id") == session_id and session.get("status") == "active":
                session["status"] = status
                session["ended_at"] = _stamp()
        _write(SESSIONS_FILE, sessions)


# =========================================================
# ATTENDANCE
# =========================================================

def all_attendance():
    return _read(ATTENDANCE_FILE)


def mark_attendance(session_id, student):
    """
    Record `student` present in `session_id`.

    Returns (status, detail):
      "marked"       detail = the new record
      "duplicate"    already marked in this session
      "not_in_roster" student is not on this session's roster
                      (detail = the live session holding them, if any)
      "inactive"     the session has ended or expired
    """
    student_id = str(student.get("student_id", ""))
    with FileLock():
        sessions = all_sessions()
        now = time.time()
        session = next((s for s in sessions if s.get("session_id") == session_id), None)
        if session is None or not _is_live(session, now):
            return "inactive", None

        if student_id not in session.get("student_ids", []):
            holder = next(
                (s for s in sessions
                 if _is_live(s, now) and student_id in s.get("student_ids", [])),
                None,
            )
            return "not_in_roster", holder

        session["last_heartbeat"] = now
        attendance = all_attendance()
        for record in attendance:
            if record.get("session_id") == session_id and str(record.get("student_id")) == student_id:
                _write(SESSIONS_FILE, sessions)
                return "duplicate", record

        record = {
            "student_id": student.get("student_id", ""),
            "prn": student.get("prn", ""),
            "name": student.get("name", ""),
            "date": datetime.now().strftime("%Y-%m-%d"),
            "time": datetime.now().strftime("%H:%M:%S"),
            "status": "Present",
            "recognition": "Face Recognized",
            "session_id": session_id,
            "faculty_id": session.get("faculty_id", ""),
            "faculty_name": session.get("faculty_name", ""),
            "subject": session.get("subject", ""),
            "class": session.get("class", ""),
            "division": session.get("division", ""),
        }
        attendance.append(record)
        _write(ATTENDANCE_FILE, attendance)
        _write(SESSIONS_FILE, sessions)
        return "marked", record


def session_attendance(session_id):
    return [r for r in all_attendance() if r.get("session_id") == session_id]


def student_summary(student_id):
    """
    Attendance figures for one student.

    Sessions give a real denominator: every session (ended or live) that had
    the student on its roster counts as a lecture. Older records written
    before sessions existed are counted per distinct day.
    """
    student_id = str(student_id)
    sessions = [s for s in all_sessions() if student_id in s.get("student_ids", [])]
    session_ids = {s["session_id"] for s in sessions}
    records = [r for r in all_attendance() if str(r.get("student_id")) == student_id]

    present_sessions = {r["session_id"] for r in records if r.get("session_id") in session_ids}
    legacy_days = {r.get("date") for r in records if not r.get("session_id")}

    total = len(sessions) + len(legacy_days)
    present = len(present_sessions) + len(legacy_days)
    absent = max(0, total - present)
    percentage = (present / total * 100) if total else 0
    return {"total": total, "present": present, "absent": absent, "percentage": percentage}
