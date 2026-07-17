"""
Hydration Buddy — A desktop water reminder app with a pixel art character.
Your personal hydration companion that pops up to remind you to drink water!

Features:
- Choose between 30 min or 1 hour reminder intervals
- Animated video or static PNG character modes
- Thought bubble with "Time to drink water!" message
- Snooze for 10 minutes
- "Great job!" acknowledgment when you drink
"""

import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import os
import sys

# Try to import OpenCV for video support
try:
    import cv2
    HAS_OPENCV = True
except ImportError:
    HAS_OPENCV = False


# ── Paths ──────────────────────────────────────────────
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ASSETS_DIR = os.path.join(BASE_DIR, "assets")
CHARACTER_PNG = os.path.join(ASSETS_DIR, "character.png")
CHARACTER_DRINKING_PNG = os.path.join(ASSETS_DIR, "character_drinking.png")
CHARACTER_VIDEO = os.path.join(ASSETS_DIR, "character_walk.mp4")

# ── Colors ─────────────────────────────────────────────
BG_WHITE = "#FFFFFF"
ACCENT_BLUE = "#2196F3"
GREEN = "#4CAF50"
ORANGE = "#FF9800"
DARK_TEXT = "#1a1a2e"
WATER_BLUE = "#0277BD"


class WaterReminderApp:
    """Main application class for the Hydration Buddy."""

    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Hydration Buddy 💧")
        self.root.geometry("360x280")
        self.root.resizable(False, False)
        self.root.configure(bg=BG_WHITE)

        # Center the window
        self.root.eval("tk::PlaceWindow . center")

        # State
        self.interval_var = tk.IntVar(value=30)
        self.media_var = tk.StringVar(value="video" if HAS_OPENCV else "image")
        self.cap = None
        self.vid_photo = None
        self.char_photo = None

        self._build_settings_ui()

    # ── Settings UI ────────────────────────────────────
    def _build_settings_ui(self):
        """Build the main settings window."""
        # Title
        tk.Label(
            self.root,
            text="💧 Hydration Buddy",
            font=("Segoe UI", 16, "bold"),
            bg=BG_WHITE,
            fg=DARK_TEXT,
        ).pack(pady=(20, 5))

        tk.Label(
            self.root,
            text="Your personal water reminder",
            font=("Segoe UI", 9),
            bg=BG_WHITE,
            fg="#666",
        ).pack(pady=(0, 15))

        # ── Interval Selection ──
        tk.Label(
            self.root,
            text="Remind me every:",
            font=("Segoe UI", 11, "bold"),
            bg=BG_WHITE,
            fg=DARK_TEXT,
        ).pack(pady=(5, 5))

        time_frame = tk.Frame(self.root, bg=BG_WHITE)
        time_frame.pack()

        tk.Radiobutton(
            time_frame, text="30 Minutes", variable=self.interval_var, value=30,
            bg=BG_WHITE, font=("Segoe UI", 10), activebackground=BG_WHITE,
            selectcolor=BG_WHITE,
        ).pack(side=tk.LEFT, padx=10)
        tk.Radiobutton(
            time_frame, text="1 Hour", variable=self.interval_var, value=60,
            bg=BG_WHITE, font=("Segoe UI", 10), activebackground=BG_WHITE,
            selectcolor=BG_WHITE,
        ).pack(side=tk.LEFT, padx=10)

        # ── Media Selection ──
        tk.Label(
            self.root,
            text="Buddy style:",
            font=("Segoe UI", 11, "bold"),
            bg=BG_WHITE,
            fg=DARK_TEXT,
        ).pack(pady=(15, 5))

        media_frame = tk.Frame(self.root, bg=BG_WHITE)
        media_frame.pack()

        if HAS_OPENCV:
            tk.Radiobutton(
                media_frame, text="🎬 Animated", variable=self.media_var, value="video",
                bg=BG_WHITE, font=("Segoe UI", 10), activebackground=BG_WHITE,
                selectcolor=BG_WHITE,
            ).pack(side=tk.LEFT, padx=10)
        else:
            tk.Label(
                media_frame,
                text="⚠️ Install opencv-python for animated mode",
                font=("Segoe UI", 8),
                bg=BG_WHITE,
                fg="#999",
            ).pack(side=tk.LEFT, padx=10)

        tk.Radiobutton(
            media_frame, text="🖼️ Static", variable=self.media_var, value="image",
            bg=BG_WHITE, font=("Segoe UI", 10), activebackground=BG_WHITE,
            selectcolor=BG_WHITE,
        ).pack(side=tk.LEFT, padx=10)

        # ── Start Button ──
        tk.Button(
            self.root,
            text="🚀 Start Reminding Me!",
            command=self.start_timer,
            bg=ACCENT_BLUE,
            fg="white",
            font=("Segoe UI", 11, "bold"),
            bd=0,
            padx=20,
            pady=8,
            cursor="hand2",
            activebackground="#1976D2",
            activeforeground="white",
        ).pack(pady=20)

    # ── Timer Logic ────────────────────────────────────
    def start_timer(self):
        """Hide settings and schedule the first reminder."""
        interval_minutes = self.interval_var.get()
        self.root.withdraw()  # Hide settings window
        self.schedule_reminder(interval_minutes * 60)

    def schedule_reminder(self, seconds: int):
        """Schedule a reminder after `seconds` seconds."""
        self.root.after(seconds * 1000, self.show_reminder)

    # ── Reminder Popup ─────────────────────────────────
    def show_reminder(self):
        """Show the reminder popup with character and buttons."""
        self.reminder_win = tk.Toplevel(self.root)
        self.reminder_win.overrideredirect(True)  # Borderless
        self.reminder_win.attributes("-topmost", True)
        self.reminder_win.configure(bg=BG_WHITE)

        # Position in bottom-right corner
        screen_w = self.reminder_win.winfo_screenwidth()
        screen_h = self.reminder_win.winfo_screenheight()
        win_w, win_h = 300, 420
        x = screen_w - win_w - 20
        y = screen_h - win_h - 40
        self.reminder_win.geometry(f"{win_w}x{win_h}+{x}+{y}")

        # Make it draggable
        self._make_draggable(self.reminder_win)

        # ── Thought Bubble ──
        bubble_frame = tk.Frame(self.reminder_win, bg=BG_WHITE)
        bubble_frame.pack(pady=(15, 5))

        # Canvas for speech bubble effect
        canvas = tk.Canvas(
            bubble_frame, width=240, height=65,
            bg=BG_WHITE, highlightthickness=0,
        )
        canvas.pack()

        # Rounded rectangle bubble
        self._draw_rounded_rect(
            canvas, 0, 5, 240, 55, radius=20,
            fill="#E3F2FD", outline="#BBDEFB",
        )
        canvas.create_text(
            120, 30, text="💧 Time to drink water!",
            font=("Segoe UI", 12, "bold"),
            fill=WATER_BLUE,
        )

        # ── Character Display ──
        self.media_label = tk.Label(self.reminder_win, bg=BG_WHITE)
        self.media_label.pack(pady=(5, 10))

        choice = self.media_var.get()
        if choice == "video" and HAS_OPENCV:
            self._start_video()
        else:
            self._show_static_image()

        # ── Buttons ──
        btn_frame = tk.Frame(self.reminder_win, bg=BG_WHITE)
        btn_frame.pack(pady=(0, 5))

        tk.Button(
            btn_frame, text="✅ Yes, I drank it!",
            command=self.drank_water,
            bg=GREEN, fg="white",
            font=("Segoe UI", 10, "bold"),
            bd=0, padx=12, pady=6,
            cursor="hand2",
            activebackground="#388E3C",
        ).grid(row=0, column=0, padx=5)

        tk.Button(
            btn_frame, text="⏰ Snooze (10 min)",
            command=self.snooze,
            bg=ORANGE, fg="white",
            font=("Segoe UI", 10, "bold"),
            bd=0, padx=12, pady=6,
            cursor="hand2",
            activebackground="#F57C00",
        ).grid(row=0, column=1, padx=5)

        # ── Close ──
        tk.Button(
            self.reminder_win, text="Close App",
            command=self.close_app,
            fg="#999", bg=BG_WHITE, bd=0,
            font=("Segoe UI", 8, "underline"),
            cursor="hand2",
        ).pack(side=tk.BOTTOM, pady=5)

    # ── Static Image ───────────────────────────────────
    def _show_static_image(self):
        """Display the static PNG character."""
        try:
            # Try drinking pose first if exists, else standing
            png_path = CHARACTER_DRINKING_PNG
            if not os.path.exists(png_path):
                png_path = CHARACTER_PNG

            if os.path.exists(png_path):
                img = Image.open(png_path)
                img = img.resize((180, 280), Image.LANCZOS)
                self.char_photo = ImageTk.PhotoImage(img)
                self.media_label.config(image=self.char_photo)
            else:
                self.media_label.config(
                    text="[Character image missing]\nPlace character.png in assets/",
                    font=("Segoe UI", 10),
                    fg="red",
                )
        except Exception as e:
            self.media_label.config(
                text=f"[Error loading image: {e}]",
                font=("Segoe UI", 9),
                fg="red",
            )

    # ── Video Playback ─────────────────────────────────
    def _start_video(self):
        """Start video playback loop."""
        if os.path.exists(CHARACTER_VIDEO):
            self.cap = cv2.VideoCapture(CHARACTER_VIDEO)
            if self.cap.isOpened():
                self.play_video()
            else:
                self.media_label.config(
                    text="[Cannot open video]",
                    font=("Segoe UI", 10),
                    fg="red",
                )
        else:
            self.media_label.config(
                text="[character_walk.mp4 missing]\nPlace video in assets/",
                font=("Segoe UI", 10),
                fg="red",
            )

    def play_video(self):
        """Play next frame of the video in a loop."""
        if (
            hasattr(self, "reminder_win")
            and self.reminder_win.winfo_exists()
            and self.cap
        ):
            ret, frame = self.cap.read()
            if not ret:
                # Loop back to start
                self.cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                ret, frame = self.cap.read()

            if ret:
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                frame = cv2.resize(frame, (180, 280))
                img = Image.fromarray(frame)
                self.vid_photo = ImageTk.PhotoImage(image=img)
                self.media_label.config(image=self.vid_photo)
                self.reminder_win.after(33, self.play_video)

    def clean_up_video(self):
        """Release video capture resources."""
        if self.cap:
            self.cap.release()
            self.cap = None

    # ── Button Actions ─────────────────────────────────
    def drank_water(self):
        """Handle 'I drank it!' — close reminder and ask next interval."""
        self.clean_up_video()
        self.reminder_win.destroy()
        self.ask_next_interval()

    def snooze(self):
        """Snooze: remind again in 10 minutes."""
        self.clean_up_video()
        self.reminder_win.destroy()
        self.schedule_reminder(10 * 60)

    def close_app(self):
        """Close the entire application."""
        self.clean_up_video()
        self.root.quit()

    # ── Follow-up Window ───────────────────────────────
    def ask_next_interval(self):
        """Show 'Great job!' follow-up with next interval options."""
        self.next_win = tk.Toplevel(self.root)
        self.next_win.title("Next Reminder")
        self.next_win.geometry("300x140")
        self.next_win.attributes("-topmost", True)
        self.next_win.configure(bg=BG_WHITE)
        self.next_win.eval(f"tk::PlaceWindow {str(self.next_win)} center")
        self.next_win.resizable(False, False)

        tk.Label(
            self.next_win,
            text="🎉 Great job staying hydrated!",
            font=("Segoe UI", 11, "bold"),
            bg=BG_WHITE,
            fg=DARK_TEXT,
        ).pack(pady=(15, 5))

        tk.Label(
            self.next_win,
            text="When should I remind you next?",
            font=("Segoe UI", 10),
            bg=BG_WHITE,
            fg="#666",
        ).pack(pady=(0, 15))

        btn_frame = tk.Frame(self.next_win, bg=BG_WHITE)
        btn_frame.pack()

        tk.Button(
            btn_frame, text="30 Mins",
            command=lambda: self.set_next(30),
            bg=ACCENT_BLUE, fg="white",
            font=("Segoe UI", 10, "bold"),
            bd=0, padx=15, pady=6,
            cursor="hand2",
        ).pack(side=tk.LEFT, padx=10)

        tk.Button(
            btn_frame, text="1 Hour",
            command=lambda: self.set_next(60),
            bg=ACCENT_BLUE, fg="white",
            font=("Segoe UI", 10, "bold"),
            bd=0, padx=15, pady=6,
            cursor="hand2",
        ).pack(side=tk.LEFT, padx=10)

    def set_next(self, minutes: int):
        """Set the next reminder and close the follow-up."""
        self.next_win.destroy()
        self.schedule_reminder(minutes * 60)

    # ── UI Helpers ─────────────────────────────────────
    @staticmethod
    def _draw_rounded_rect(
        canvas: tk.Canvas, x1, y1, x2, y2, radius=20, **kwargs
    ):
        """Draw a rounded rectangle on a canvas."""
        points = [
            x1 + radius, y1,
            x2 - radius, y1,
            x2, y1,
            x2, y1 + radius,
            x2, y2 - radius,
            x2, y2,
            x2 - radius, y2,
            x1 + radius, y2,
            x1, y2,
            x1, y2 - radius,
            x1, y1 + radius,
            x1, y1,
        ]
        canvas.create_polygon(points, smooth=True, **kwargs)

    def _make_draggable(self, window: tk.Toplevel):
        """Make a borderless window draggable by clicking anywhere."""

        def start_move(event):
            window._drag_x = event.x
            window._drag_y = event.y

        def do_move(event):
            x = window.winfo_x() + event.x - window._drag_x
            y = window.winfo_y() + event.y - window._drag_y
            window.geometry(f"+{x}+{y}")

        window.bind("<Button-1>", start_move)
        window.bind("<B1-Motion>", do_move)


# ── Entry Point ────────────────────────────────────────
if __name__ == "__main__":
    root = tk.Tk()
    app = WaterReminderApp(root)
    root.mainloop()
