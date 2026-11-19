"""
Guided face capture for student registration.

Works like the photo step of an official identity-verification flow:

1. A guidelines dialog lists the rules for an acceptable photograph and the
   student must confirm they have read them.
2. A live camera screen shows an oval guide and a checklist that ticks off in
   real time (one face, centred, distance, head straight, eyes visible, even
   lighting, sharpness). The photo is taken automatically once every check
   has passed and the student has held still for a moment.
3. The student reviews the photo and accepts it or retakes it.
"""

import collections
import time

import cv2
import customtkinter as ctk
import numpy as np

from theme import (
    fit_geometry, cascade_path,
    BG_COLOR, BORDER_COLOR, CV_BAD, CV_GOLD, CV_GOLD_LIGHT, CV_INK, CV_OK,
    CV_WARN, CV_WHITE, DANGER, FONT_BODY, FONT_HEAD, GOLD, GOLD_DEEP,
    GOLD_LIGHT, INK, LIGHT_GREY, MUTED_TEXT, PRIMARY, PRIMARY_HOVER, TEXT_COLOR,
    TINT, WHITE, GradientLine,
)


# =========================================================
# THE RULES SHOWN TO THE STUDENT
# =========================================================

GUIDELINES = [
    ("01", "Face the camera directly",
     "Keep your head straight and look into the camera lens. "
     "Do not tilt or turn your head."),
    ("02", "Neutral expression",
     "Keep both eyes open and your mouth closed. "
     "Do not smile broadly, squint or look away."),
    ("03", "Nothing covering the face",
     "Remove sunglasses, caps, masks and scarves. Hair must not cover "
     "your eyes or eyebrows."),
    ("04", "Even, front lighting",
     "Face a window or light source. Avoid shadows on the face and "
     "strong light behind you."),
    ("05", "Plain background",
     "Stand in front of a plain, light wall. No other person or "
     "object should appear in the frame."),
    ("06", "Correct distance",
     "Sit about an arm's length from the camera so that your face "
     "fills the oval guide."),
    ("07", "Stay still",
     "Hold steady until the progress bar completes. A blurred photo "
     "will not be accepted."),
    ("08", "Live photograph only",
     "Photos of photos, screens or another person are not permitted "
     "and may lead to rejection of your registration."),
]


# =========================================================
# GUIDELINES DIALOG
# =========================================================

class GuidelinesDialog(ctk.CTkToplevel):
    """Modal dialog. After wait_window(), `.accepted` tells the outcome."""

    def __init__(self, parent, student_name=""):
        super().__init__(parent, fg_color=BG_COLOR)
        self.accepted = False
        self.title("Photograph Guidelines")
        self.resizable(False, True)
        fit_geometry(self, 860, 690)
        self.minsize(700, 420)

        self._build(student_name)
        self.protocol("WM_DELETE_WINDOW", self._cancel)
        self.after(150, self._take_focus)

    def _take_focus(self):
        try:
            self.lift()
            self.focus_force()
            self.grab_set()
        except Exception:
            pass

    # ---- layout -------------------------------------------------------
    def _build(self, student_name):
        header = ctk.CTkFrame(self, fg_color=INK, corner_radius=0, height=104)
        header.pack(fill="x")
        header.pack_propagate(False)

        ctk.CTkLabel(
            header, text="IDENTITY VERIFICATION  •  STEP 1 OF 2",
            font=(FONT_BODY, 11, "bold"), text_color=GOLD_LIGHT,
        ).pack(anchor="w", padx=34, pady=(18, 0))
        ctk.CTkLabel(
            header, text="Photograph Capture Guidelines",
            font=(FONT_HEAD, 26, "bold"), text_color=WHITE,
        ).pack(anchor="w", padx=34)
        who = f"for {student_name}" if student_name else ""
        ctk.CTkLabel(
            header,
            text=f"Please read every instruction carefully before the camera opens {who}".strip(),
            font=(FONT_BODY, 12), text_color="#B4BCD3",
        ).pack(anchor="w", padx=34, pady=(2, 0))

        GradientLine(self, height=3, bg=BG_COLOR).pack(fill="x")

        foot = ctk.CTkFrame(self, fg_color=BG_COLOR, corner_radius=0)
        foot.pack(side="bottom", fill="x")
        body = ctk.CTkScrollableFrame(self, fg_color="transparent")
        body.pack(side="top", fill="both", expand=True, padx=14, pady=(10, 0))
        grid = ctk.CTkFrame(body, fg_color="transparent")
        grid.pack(fill="x", padx=14, pady=(6, 6))
        grid.grid_columnconfigure((0, 1), weight=1, uniform="col")

        for index, (number, title, text) in enumerate(GUIDELINES):
            self._rule_card(grid, number, title, text).grid(
                row=index // 2, column=index % 2, padx=6, pady=5, sticky="nsew")

        note = ctk.CTkFrame(body, fg_color="#F7EBD6", corner_radius=12,
                            border_width=1, border_color=GOLD)
        note.pack(fill="x", padx=34, pady=(6, 8))
        ctk.CTkLabel(
            note, anchor="w", justify="left", wraplength=715,
            font=(FONT_BODY, 11), text_color=TEXT_COLOR,
            text=("Important:  your photograph is stored with your registration and is "
                  "used to verify your identity when attendance is marked. It must be a "
                  "clear, recent, unaltered image of your own face."),
        ).pack(fill="x", padx=16, pady=10)

        self.agree_var = ctk.BooleanVar(value=False)
        ctk.CTkCheckBox(
            foot,
            text="I have read and understood these instructions and confirm that "
                 "the photograph will be of my own face.",
            variable=self.agree_var, command=self._toggle,
            font=(FONT_BODY, 12), text_color=TEXT_COLOR,
            fg_color=INK, hover_color=PRIMARY_HOVER, border_color=GOLD_DEEP,
            checkmark_color=GOLD_LIGHT,
        ).pack(anchor="w", padx=36, pady=(2, 10))

        buttons = ctk.CTkFrame(foot, fg_color="transparent")
        buttons.pack(fill="x", padx=34, pady=(0, 18))
        ctk.CTkButton(
            buttons, text="Cancel", width=130, height=44, corner_radius=22,
            fg_color="transparent", border_width=1, border_color=BORDER_COLOR,
            text_color=MUTED_TEXT, hover_color=LIGHT_GREY,
            font=(FONT_BODY, 13, "bold"), command=self._cancel,
        ).pack(side="right", padx=(10, 0))
        self.continue_btn = ctk.CTkButton(
            buttons, text="I Agree  •  Open Camera", width=230, height=44,
            corner_radius=22, fg_color=GOLD, hover_color=GOLD_LIGHT,
            text_color=INK, text_color_disabled="#8E8A7D",
            font=(FONT_BODY, 13, "bold"), state="disabled", command=self._accept,
        )
        self.continue_btn.pack(side="right")

    def _rule_card(self, parent, number, title, text):
        card = ctk.CTkFrame(parent, fg_color=WHITE, corner_radius=14,
                            border_width=1, border_color=BORDER_COLOR)
        badge = ctk.CTkFrame(card, width=46, height=46, corner_radius=23,
                             fg_color=INK)
        badge.pack(side="left", padx=(14, 12), pady=12, anchor="n")
        badge.pack_propagate(False)
        ctk.CTkLabel(
            badge, text=number, fg_color="transparent",
            text_color=GOLD_LIGHT, font=(FONT_HEAD, 14, "bold"),
        ).pack(expand=True)
        body = ctk.CTkFrame(card, fg_color="transparent")
        body.pack(side="left", fill="both", expand=True, pady=10, padx=(0, 12))
        ctk.CTkLabel(body, text=title, anchor="w", font=(FONT_BODY, 13, "bold"),
                     text_color=INK).pack(fill="x")
        ctk.CTkLabel(body, text=text, anchor="w", justify="left", wraplength=250,
                     font=(FONT_BODY, 11), text_color=MUTED_TEXT).pack(fill="x", pady=(2, 0))
        return card

    # ---- actions ------------------------------------------------------
    def _toggle(self):
        self.continue_btn.configure(
            state="normal" if self.agree_var.get() else "disabled")

    def _accept(self):
        if self.agree_var.get():
            self.accepted = True
            self.destroy()

    def _cancel(self):
        self.accepted = False
        self.destroy()


def show_guidelines(parent, student_name=""):
    """Show the guidelines and return True if the student accepted them."""
    dialog = GuidelinesDialog(parent, student_name)
    parent.wait_window(dialog)
    return dialog.accepted


# =========================================================
# LIVE QUALITY ANALYSIS
# =========================================================

CHECKS = [
    ("single", "One face in frame"),
    ("centred", "Face centred in oval"),
    ("distance", "Correct distance"),
    ("straight", "Head straight"),
    ("eyes", "Eyes open, looking at camera"),
    ("light", "Even lighting"),
    ("sharp", "Image sharp, no movement"),
]

HINTS = {
    "single": "Make sure only your face is in the frame",
    "centred": "Move your face into the centre of the oval",
    "distance": "Adjust your distance from the camera",
    "straight": "Keep your head straight, do not tilt",
    "eyes": "Open your eyes and look into the camera",
    "light": "Improve the lighting on your face",
    "sharp": "Hold still, the image is blurred",
}

HOLD_SECONDS = 1.8


class FaceQuality:
    """Runs the verification checks on camera frames."""

    def __init__(self):
        self.face = cv2.CascadeClassifier(cascade_path("haarcascade_frontalface_default.xml"))
        self.eye = cv2.CascadeClassifier(cascade_path("haarcascade_eye.xml"))
        self.history = {key: collections.deque(maxlen=5) for key, _ in CHECKS}
        self.detail = {}

    @staticmethod
    def oval(shape):
        h, w = shape[:2]
        return (int(w * 0.5), int(h * 0.47)), (int(w * 0.215), int(h * 0.37))

    def analyse(self, frame):
        """Return (raw_results, face_box_or_None) for one frame."""
        h, w = frame.shape[:2]
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        (ocx, ocy), (oax, oay) = self.oval(frame.shape)

        faces = self.face.detectMultiScale(
            gray, scaleFactor=1.1, minNeighbors=6, minSize=(int(h * 0.22), int(h * 0.22)))
        res = {key: False for key, _ in CHECKS}
        self.detail = {}
        res["single"] = len(faces) == 1
        if len(faces) != 1:
            self.detail["single"] = "none" if len(faces) == 0 else "many"
            return res, (faces[0] if len(faces) else None)

        x, y, fw, fh = [int(v) for v in faces[0]]
        fcx, fcy = x + fw / 2, y + fh / 2

        # centred inside the guide
        res["centred"] = abs(fcx - ocx) < w * 0.085 and abs(fcy - ocy) < h * 0.10

        # distance: face height relative to the frame
        ratio = fh / h
        res["distance"] = 0.36 <= ratio <= 0.62
        self.detail["distance"] = "far" if ratio < 0.36 else ("near" if ratio > 0.62 else "ok")

        roi = gray[y:y + fh, x:x + fw]

        # eyes visible, and head tilt from the eye line
        upper = roi[int(fh * 0.12):int(fh * 0.60), :]
        eyes = self.eye.detectMultiScale(
            upper, scaleFactor=1.1, minNeighbors=5,
            minSize=(max(14, fw // 9), max(14, fw // 9)))
        eyes = sorted(eyes, key=lambda e: -e[2] * e[3])[:2]
        res["eyes"] = len(eyes) == 2 and abs(
            (eyes[0][0] + eyes[0][2] / 2) - (eyes[1][0] + eyes[1][2] / 2)) > fw * 0.22
        if res["eyes"]:
            (ax, ay, aw, ah), (bx, by, bw, bh) = eyes
            dx = abs((ax + aw / 2) - (bx + bw / 2))
            dy = abs((ay + ah / 2) - (by + bh / 2))
            res["straight"] = dy / max(dx, 1) < 0.16
        else:
            # frontal detector already implies a roughly frontal face; without
            # visible eyes we cannot confirm the head is level
            res["straight"] = False

        # lighting: bright enough, not blown out, left/right balanced
        mean = float(roi.mean())
        left, right = float(roi[:, :fw // 2].mean()), float(roi[:, fw // 2:].mean())
        balance = abs(left - right) / max(mean, 1.0)
        res["light"] = 70 <= mean <= 205 and balance < 0.28
        self.detail["light"] = (mean, balance)

        # sharpness
        sharp = cv2.Laplacian(roi, cv2.CV_64F).var()
        res["sharp"] = sharp > 45
        self.detail["sharpness"] = sharp
        return res, (x, y, fw, fh)

    def smoothed(self, raw):
        """Majority vote over recent frames so ticks do not flicker."""
        out = {}
        for key, _ in CHECKS:
            self.history[key].append(bool(raw[key]))
            hist = self.history[key]
            out[key] = sum(hist) * 2 > len(hist)
        return out

    def reset(self):
        for dq in self.history.values():
            dq.clear()

    def hint(self, state):
        for key, _ in CHECKS:
            if not state[key]:
                if key == "distance":
                    return ("Move a little closer to the camera"
                            if self.detail.get("distance") == "far"
                            else "Move a little away from the camera")
                if key == "single" and self.detail.get("single") == "none":
                    return "No face detected - look at the camera"
                if key == "single":
                    return "More than one face - only you should be visible"
                return HINTS[key]
        return "Perfect - hold still"


# =========================================================
# DRAWING
# =========================================================

PANEL_W = 310
FONT = cv2.FONT_HERSHEY_SIMPLEX


def _text(img, text, org, scale=0.55, color=CV_WHITE, thick=1):
    cv2.putText(img, text, org, FONT, scale, color, thick, cv2.LINE_AA)


def _wrap(text, max_chars):
    words, lines, cur = text.split(), [], ""
    for word in words:
        if len(cur) + len(word) + 1 > max_chars:
            lines.append(cur)
            cur = word
        else:
            cur = (cur + " " + word).strip()
    if cur:
        lines.append(cur)
    return lines


def _icon(img, cx, cy, ok, pending):
    if pending:
        cv2.circle(img, (cx, cy), 11, (120, 110, 100), 1, cv2.LINE_AA)
        return
    color = CV_OK if ok else CV_BAD
    cv2.circle(img, (cx, cy), 11, color, -1, cv2.LINE_AA)
    if ok:
        pts = np.array([[cx - 5, cy], [cx - 1, cy + 4], [cx + 6, cy - 4]], np.int32)
        cv2.polylines(img, [pts], False, CV_WHITE, 2, cv2.LINE_AA)
    else:
        cv2.line(img, (cx - 4, cy - 4), (cx + 4, cy + 4), CV_WHITE, 2, cv2.LINE_AA)
        cv2.line(img, (cx + 4, cy - 4), (cx - 4, cy + 4), CV_WHITE, 2, cv2.LINE_AA)


def render(frame, state, hint, hold, student, checker, face_box=None, flash=0.0):
    """Compose the camera view + verification panel."""
    h, w = frame.shape[:2]
    view = frame.copy()
    all_ok = all(state.values())
    passed = sum(state.values())

    # dim everything outside the oval guide
    (cx, cy), axes = checker.oval(frame.shape)
    mask = np.zeros((h, w), np.uint8)
    cv2.ellipse(mask, (cx, cy), axes, 0, 0, 360, 255, -1)
    dim = (view * 0.38).astype(np.uint8)
    view = np.where(mask[..., None] > 0, view, dim)

    ring = CV_OK if all_ok else (CV_WARN if passed >= 4 else CV_BAD)
    cv2.ellipse(view, (cx, cy), axes, 0, 0, 360, ring, 3, cv2.LINE_AA)
    cv2.ellipse(view, (cx, cy), (axes[0] + 9, axes[1] + 9), 0, 0, 360, CV_GOLD, 1, cv2.LINE_AA)

    # corner brackets
    m, L = 18, 30
    for (x, y, dx, dy) in ((m, m, 1, 1), (w - m, m, -1, 1), (m, h - m, 1, -1), (w - m, h - m, -1, -1)):
        cv2.polylines(view, [np.array([[x, y + dy * L], [x, y], [x + dx * L, y]], np.int32)],
                      False, CV_GOLD, 2, cv2.LINE_AA)

    # hint bar
    bar_h = 46
    cv2.rectangle(view, (0, h - bar_h), (w, h), CV_INK, -1)
    cv2.line(view, (0, h - bar_h), (w, h - bar_h), CV_GOLD, 2)
    size = cv2.getTextSize(hint, FONT, 0.62, 2)[0]
    _text(view, hint, ((w - size[0]) // 2, h - 17), 0.62,
          CV_OK if all_ok else CV_WHITE, 2)

    if hold > 0:
        cv2.rectangle(view, (cx - 110, cy + axes[1] + 14), (cx + 110, cy + axes[1] + 22), (60, 55, 50), -1)
        cv2.rectangle(view, (cx - 110, cy + axes[1] + 14),
                      (cx - 110 + int(220 * min(hold, 1.0)), cy + axes[1] + 22), CV_OK, -1)

    if flash > 0:
        view = cv2.addWeighted(view, 1 - flash, np.full_like(view, 255), flash, 0)

    # side panel
    panel = np.full((h, PANEL_W, 3), CV_INK, np.uint8)
    cv2.line(panel, (0, 0), (0, h), CV_GOLD, 2)
    _text(panel, "IDENTITY PHOTO CHECK", (22, 38), 0.55, CV_GOLD_LIGHT, 1)
    _text(panel, (student or "Student")[:26], (22, 66), 0.62, CV_WHITE, 1)
    cv2.line(panel, (22, 82), (PANEL_W - 22, 82), (90, 80, 70), 1)

    y = 112
    for key, label in CHECKS:
        pending = key not in state
        _icon(panel, 36, y - 5, state.get(key, False), pending)
        _text(panel, label, (58, y), 0.5, CV_WHITE if state.get(key) else (190, 190, 200), 1)
        y += 37

    cv2.line(panel, (22, h - 118), (PANEL_W - 22, h - 118), (90, 80, 70), 1)
    _text(panel, f"{passed} of {len(CHECKS)} checks passed", (22, h - 92), 0.5, CV_GOLD_LIGHT, 1)
    for i, line in enumerate(_wrap("Photo is taken automatically once every check "
                                   "is green.  Press Q or ESC to cancel.", 34)):
        _text(panel, line, (22, h - 66 + i * 20), 0.42, (170, 170, 185), 1)

    return np.hstack([view, panel])


def _review(frame, student):
    """Return the review screen image."""
    h, w = frame.shape[:2]
    view = frame.copy()
    cv2.rectangle(view, (0, h - 52), (w, h), CV_INK, -1)
    cv2.line(view, (0, h - 52), (w, h - 52), CV_GOLD, 2)
    _text(view, "ENTER = Accept photo     R = Retake     Q = Cancel", (30, h - 19), 0.62, CV_WHITE, 2)
    panel = np.full((h, PANEL_W, 3), CV_INK, np.uint8)
    cv2.line(panel, (0, 0), (0, h), CV_GOLD, 2)
    _text(panel, "REVIEW YOUR PHOTO", (22, 38), 0.55, CV_GOLD_LIGHT, 1)
    _text(panel, (student or "Student")[:26], (22, 66), 0.62, CV_WHITE, 1)
    y = 120
    for line in _wrap("Check that your whole face is clearly visible, eyes are open "
                      "and there are no shadows or reflections.", 30):
        _text(panel, line, (22, y), 0.5, CV_WHITE, 1)
        y += 26
    y += 14
    for line in _wrap("If anything is wrong, press R and take the photo again.", 30):
        _text(panel, line, (22, y), 0.46, (170, 170, 185), 1)
        y += 24
    return np.hstack([view, panel])


# =========================================================
# CAPTURE LOOP
# =========================================================

WINDOW = "Face Capture - Identity Verification"


def _bring_to_front():
    """Make sure the OpenCV window is on top of the (maximised) Tk window."""
    try:
        cv2.moveWindow(WINDOW, 60, 30)
    except Exception:
        pass
    try:
        cv2.setWindowProperty(WINDOW, cv2.WND_PROP_TOPMOST, 1)
    except Exception:
        pass
    try:                                              # Windows: force foreground
        import ctypes
        hwnd = ctypes.windll.user32.FindWindowW(None, WINDOW)
        if hwnd:
            ctypes.windll.user32.ShowWindow(hwnd, 9)
            ctypes.windll.user32.SetForegroundWindow(hwnd)
    except Exception:
        pass


def open_camera():
    cap = None
    for index in (0, 1):
        for backend in (getattr(cv2, "CAP_DSHOW", cv2.CAP_ANY), cv2.CAP_ANY):
            cap = cv2.VideoCapture(index, backend)
            if cap.isOpened():
                cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
                cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
                return cap
            cap.release()
    return None


def capture_face(student_name="", camera_factory=open_camera, checker=None,
                 hold_seconds=HOLD_SECONDS, show=True):
    """
    Run the guided capture. Returns the captured BGR frame (un-mirrored,
    exactly as the camera saw it), or None if cancelled or the camera failed.
    Raises RuntimeError("camera") if no camera could be opened.
    """
    cap = camera_factory()
    if cap is None:
        raise RuntimeError("camera")

    checker = checker or FaceQuality()
    result = None
    try:
        if show:
            cv2.namedWindow(WINDOW, cv2.WINDOW_AUTOSIZE)
        hold_start = None
        frames = 0
        close_detect = None          # decided after warm-up (build-dependent)
        while True:
            ok, raw = cap.read()
            if not ok:
                frames += 1
                if frames < 60:                   # cameras need a moment to warm up
                    time.sleep(0.03)
                    continue
                raise RuntimeError("camera")
            frames += 1
            mirrored = cv2.flip(raw, 1)          # natural "mirror" for the student

            raw_checks, box = checker.analyse(mirrored)
            state = checker.smoothed(raw_checks)
            all_ok = all(state.values())

            now = time.time()
            if all_ok:
                hold_start = hold_start or now
                hold = (now - hold_start) / hold_seconds
            else:
                hold_start, hold = None, 0.0

            hint = checker.hint(state)
            if show:
                cv2.imshow(WINDOW, render(mirrored, state, hint, hold, student_name, checker, box))
                key = cv2.waitKey(1) & 0xFF
                if frames == 3:
                    _bring_to_front()
                if frames == 20:                  # does this build report visibility?
                    close_detect = _visible(WINDOW) >= 1
                if close_detect and _visible(WINDOW) < 1:
                    break
            else:
                key = 255

            if key in (27, ord("q"), ord("Q")):
                break

            manual = key == 32 and all_ok
            if hold >= 1.0 or manual:
                candidate = raw.copy()
                if show:
                    for flash in (0.9, 0.6, 0.3):
                        cv2.imshow(WINDOW, render(mirrored, state, "Captured", 1.0,
                                                  student_name, checker, box, flash))
                        cv2.waitKey(30)
                    decision = _review_loop(candidate, student_name)
                else:
                    decision = "accept"
                if decision == "accept":
                    result = candidate
                    break
                if decision == "cancel":
                    break
                checker.reset()
                hold_start = None
    finally:
        cap.release()
        if show:
            cv2.destroyAllWindows()
    return result


def _visible(name):
    try:
        return cv2.getWindowProperty(name, cv2.WND_PROP_VISIBLE)
    except Exception:
        return 1


def _review_loop(mirrored, student_name):
    screen = _review(mirrored, student_name)
    while True:
        cv2.imshow(WINDOW, screen)
        key = cv2.waitKey(30) & 0xFF
        if key in (13, 10, 32):
            return "accept"
        if key in (ord("r"), ord("R")):
            return "retake"
        if key in (27, ord("q"), ord("Q")):
            return "cancel"