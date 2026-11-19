# AI Based Smart Attendance System

An AI-based smart attendance system that uses face recognition and image processing to automatically identify registered individuals and record their attendance.

## 📌 About the Project

Traditional attendance methods such as manual registers can be time-consuming, error-prone, and vulnerable to proxy attendance.

This project aims to provide a simple, contactless attendance system using a computer webcam. The system captures facial images, recognizes registered individuals, and automatically records their name, date, and time of attendance.

## 🛠️ Technology Stack

- Python
- OpenCV
- Face Recognition
- CustomTkinter
- CSV

## ✨ Planned Features

- Student registration
- Face capture through webcam
- Face recognition
- Automatic attendance marking
- Attendance records with date and time
- View attendance records through the application
- Simple and user-friendly graphical interface

## 📂 Project Structure

```text
AI-Smart-Attendance-System/
│
├── src/
├── data/
├── assets/
├── tests/
├── docs/
│
├── README.md
├── requirements.txt
├── .gitignore
└── LICENSE
```

## 🆕 What's New

**Redesigned interface** – a shared theme (`src/theme.py`): ivory, midnight navy and antique gold, serif headings, gradient rules, an animated face-scan hero and a fade-in on every window. Change the palette in one file.

**Guided face capture** (`src/face_capture.py`) – before the camera opens, the student reads an official-style list of photo rules and must confirm them. The camera screen then verifies the photo live (one face, centred, distance, head straight, eyes open, even lighting, sharpness), captures automatically when every check is green, and lets the student review or retake.

**Several faculty at once** (`src/session_store.py`, `src/session_ui.py`) – each faculty member starts a *session* (subject + class/division + chosen students). Any number of sessions can be live together, but a student can be in only one live session at a time; students held by another faculty are locked and shown with the faculty's name. Writes are protected by a cross-process file lock, and a session that stops responding expires after 75 seconds so students are never locked out.

Run flow: `home.py` → `login.py` (faculty account) → `main.py` (registration) → **Take Attendance** button (dashboard). Open the dashboard on each faculty's own computer or window; all of them must share the same `src` folder so they see each other's sessions.

## 🚧 Project Status

Currently under development.

## 👥 Team Members

- Prachi Phulari
- Meera Sase
- Vidhi Sharma
- Tanisha Patil

## 📜 License

This project is developed for academic and educational purposes.