"""
Hydration Buddy — Desktop Pet Edition
A transparent, floating pixel art character that reminds you to drink water!

Uses Win32 UpdateLayeredWindow for true per-pixel alpha transparency.
The character floats on your desktop like a pet/mascot with no background.
"""

import tkinter as tk
from PIL import Image, ImageDraw, ImageFont, ImageTk
import os
import sys

# Win32 for transparent layered windows
import win32gui
import win32con
import win32api
import win32ui

# Try OpenCV for video
try:
    import cv2
    import numpy as np
    HAS_OPENCV = True
except ImportError:
    HAS_OPENCV = False


# ── Paths ──────────────────────────────────────────────
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ASSETS_DIR = os.path.join(BASE_DIR, "assets")
CHARACTER_TRANSPARENT = os.path.join(ASSETS_DIR, "character_transparent.png")
CHARACTER_DRINKING_TRANSPARENT = os.path.join(ASSETS_DIR, "character_drinking_transparent.png")
CHARACTER_VIDEO = os.path.join(ASSETS_DIR, "character_walk.mp4")

# ── Layout Constants ──────────────────────────────────
CHAR_MAX_W = 200
CHAR_MAX_H = 280
WINDOW_W = 300
BUBBLE_W = 260
BUBBLE_H = 50
BTN_PANEL_H = 55
BTN_H = 36
PADDING = 8
WINDOW_H = BUBBLE_H + CHAR_MAX_H + BTN_PANEL_H + PADDING * 3


class TransparentWindow:
    """A borderless window with per-pixel alpha using UpdateLayeredWindow.
    Supports click zone detection for interactive buttons."""

    def __init__(self, width, height, x, y, click_zones=None, on_click=None):
        self.width = width
        self.height = height
        self.click_zones = click_zones or {}  # {name: (x1,y1,x2,y2)}
        self.on_click = on_click  # callback(name)
        self.drag_offset = (0, 0)
        self.dragging = False
        self.drag_threshold = 5  # pixels before it counts as a drag
        
        # Register window class
        wc = win32gui.WNDCLASS()
        wc.lpfnWndProc = self._wnd_proc
        wc.hInstance = win32api.GetModuleHandle(None)
        wc.lpszClassName = "HydrationBuddyPet"
        try:
            win32gui.RegisterClass(wc)
        except Exception:
            pass  # Already registered
        
        # Create layered window
        self.hwnd = win32gui.CreateWindowEx(
            win32con.WS_EX_LAYERED | win32con.WS_EX_TOPMOST | win32con.WS_EX_TOOLWINDOW,
            "HydrationBuddyPet",
            "Hydration Buddy",
            win32con.WS_POPUP,
            x, y, width, height,
            None, None, wc.hInstance, None,
        )
        
        # Subclass the window to handle messages
        self._old_wndproc = win32gui.SetWindowLong(
            self.hwnd, win32con.GWL_WNDPROC,
            self._make_wndproc()
        )

    def _make_wndproc(self):
        """Create a window procedure that routes messages to Python."""
        def wndproc(hwnd, msg, wparam, lparam):
            if msg == win32con.WM_LBUTTONDOWN:
                self.dragging = True
                self._click_start = (lparam & 0xFFFF, (lparam >> 16) & 0xFFFF)
                return 0
            elif msg == win32con.WM_LBUTTONUP:
                if self.dragging:
                    ex, ey = lparam & 0xFFFF, (lparam >> 16) & 0xFFFF
                    sx, sy = self._click_start
                    # Only count as click if didn't move much
                    if abs(ex - sx) < self.drag_threshold and abs(ey - sy) < self.drag_threshold:
                        self._check_click(ex, ey)
                    self.dragging = False
                return 0
            elif msg == win32con.WM_MOUSEMOVE and self.dragging:
                x, y = lparam & 0xFFFF, (lparam >> 16) & 0xFFFF
                rect = win32gui.GetWindowRect(hwnd)
                new_x = rect[0] + x - self._click_start[0]
                new_y = rect[1] + y - self._click_start[1]
                win32gui.SetWindowPos(hwnd, None, new_x, new_y, 0, 0,
                                      win32con.SWP_NOSIZE | win32con.SWP_NOZORDER)
                return 0
            elif msg == win32con.WM_RBUTTONUP:
                # Right-click to dismiss
                if self.on_click:
                    self.on_click("dismiss")
                return 0
            return win32gui.CallWindowProc(self._old_wndproc, hwnd, msg, wparam, lparam)
        return wndproc

    def _check_click(self, x, y):
        """Check if the click falls in any registered zone."""
        for name, (x1, y1, x2, y2) in self.click_zones.items():
            if x1 <= x <= x2 and y1 <= y <= y2:
                if self.on_click:
                    self.on_click(name)
                return

    def update(self, pil_image):
        """Update the window with a PIL RGBA image."""
        if pil_image.size != (self.width, self.height):
            pil_image = pil_image.resize((self.width, self.height), Image.LANCZOS)
        
        # Convert PIL RGBA to 32-bit bitmap with alpha
        bitmap_info = win32gui.GetDC(0)
        hdc_screen = win32gui.GetDC(0)
        hdc_mem = win32ui.CreateDCFromHandle(win32gui.CreateCompatibleDC(hdc_screen))
        hbm = win32ui.CreateBitmap()
        
        # Create bitmap with alpha
        rgba_data = pil_image.tobytes('raw', 'BGRA')
        hbm.CreateCompatibleBitmap(win32gui.GetDC(0), self.width, self.height)
        hbm.SetBitmapBits(rgba_data)
        
        hdc_mem.SelectObject(hbm)
        
        # Update layered window
        blend = win32gui.BLENDFUNCTION(
            win32con.AC_SRC_OVER, 0, 255, win32con.AC_SRC_ALPHA
        )
        win32gui.UpdateLayeredWindow(
            self.hwnd, hdc_screen,
            None,  # position unchanged
            (self.width, self.height),
            hdc_mem.GetSafeHdc(),
            (0, 0),  # source origin
            0,  # color key (unused with AC_SRC_ALPHA)
            blend,
            win32con.ULW_ALPHA,
        )
        
        # Cleanup
        win32gui.DeleteObject(hbm.GetSafeHandle())
        hdc_mem.DeleteDC()
        win32gui.ReleaseDC(0, hdc_screen)

    def show(self):
        """Show the window."""
        win32gui.ShowWindow(self.hwnd, win32con.SW_SHOW)

    def hide(self):
        """Hide the window."""
        win32gui.ShowWindow(self.hwnd, win32con.SW_HIDE)

    def close(self):
        """Destroy the window."""
        win32gui.DestroyWindow(self.hwnd)

    @staticmethod
    def _wnd_proc(hwnd, msg, wparam, lparam):
        """Initial window proc — gets subclassed after creation."""
        return win32gui.DefWindowProc(hwnd, msg, wparam, lparam)

    def get_position(self):
        """Get current window position."""
        rect = win32gui.GetWindowRect(self.hwnd)
        return (rect[0], rect[1])


def create_pet_frame(char_img, show_bubble=True, show_buttons=True):
    """Compose a single frame: bubble + character + buttons on transparent BG."""
    frame = Image.new('RGBA', (WINDOW_W, WINDOW_H), (0, 0, 0, 0))
    draw = ImageDraw.Draw(frame)
    current_y = PADDING
    
    # ── Thought Bubble ──
    if show_bubble:
        bx = (WINDOW_W - BUBBLE_W) // 2
        
        # Bubble background (rounded rect)
        bubble_rect = [bx, current_y, bx + BUBBLE_W, current_y + BUBBLE_H]
        draw.rounded_rectangle(bubble_rect, radius=20, fill=(227, 242, 253, 240), outline=(187, 222, 251, 255), width=2)
        
        # Droplet icon + text
        try:
            font_bubble = ImageFont.truetype("seguiemj.ttf", 20)
            font_text = ImageFont.truetype("segoeuib.ttf", 16)
        except Exception:
            font_bubble = ImageFont.load_default()
            font_text = ImageFont.load_default()
        
        draw.text((bx + 12, current_y + BUBBLE_H // 2 - 10), "💧", fill=(59, 130, 246, 255), font=font_bubble, anchor='lm')
        draw.text((bx + 40, current_y + BUBBLE_H // 2), "Time to drink water!", 
                  fill=(2, 119, 189, 255), font=font_text, anchor='lm')
        
        current_y += BUBBLE_H + PADDING
    
    # ── Character ──
    if char_img:
        # Scale to fit
        img = char_img.copy()
        img.thumbnail((CHAR_MAX_W, CHAR_MAX_H), Image.LANCZOS)
        cx = (WINDOW_W - img.width) // 2
        frame.paste(img, (cx, current_y), img)  # Use alpha mask
        current_y += img.height + PADDING
    
    # ── Buttons Panel ──
    if show_buttons:
        panel_y = WINDOW_H - BTN_PANEL_H
        
        # Semi-transparent dark panel
        panel = Image.new('RGBA', (WINDOW_W, BTN_PANEL_H), (30, 30, 30, 210))
        frame.paste(panel, (0, panel_y), panel)
        
        # Buttons
        btn_w = 125
        total_btn_w = btn_w * 2 + 10
        start_x = (WINDOW_W - total_btn_w) // 2
        btn_cy = panel_y + (BTN_PANEL_H - BTN_H) // 2
        
        # Green button - "Yes, I drank it!"
        green_rect = [start_x, btn_cy, start_x + btn_w, btn_cy + BTN_H]
        draw.rounded_rectangle(green_rect, radius=8, fill=(34, 197, 94, 255))
        try:
            font_btn = ImageFont.truetype("segoeuib.ttf", 12)
        except:
            font_btn = ImageFont.load_default()
        draw.text((start_x + btn_w // 2, btn_cy + BTN_H // 2), "✓  Yes, I drank it!",
                  fill=(255, 255, 255, 255), font=font_btn, anchor='mm')
        
        # Orange button - "Snooze (10m)"
        orange_rect = [start_x + btn_w + 10, btn_cy, start_x + btn_w * 2 + 10, btn_cy + BTN_H]
        draw.rounded_rectangle(orange_rect, radius=8, fill=(249, 115, 22, 255))
        draw.text((start_x + btn_w + 10 + btn_w // 2, btn_cy + BTN_H // 2), "⏰  Snooze (10m)",
                  fill=(255, 255, 255, 255), font=font_btn, anchor='mm')
    
    return frame


class HydrationBuddyPet:
    """Main pet application."""

    def __init__(self):
        self.root = tk.Tk()
        self.root.withdraw()
        
        self.interval_minutes = 30
        self.media_mode = "video" if HAS_OPENCV else "image"
        self.running = False
        self.pet_window = None
        self.timer_id = None
        
        # Load character images (with alpha)
        self.char_standing = None
        self.char_drinking = None
        if os.path.exists(CHARACTER_TRANSPARENT):
            self.char_standing = Image.open(CHARACTER_TRANSPARENT).convert('RGBA')
        if os.path.exists(CHARACTER_DRINKING_TRANSPARENT):
            self.char_drinking = Image.open(CHARACTER_DRINKING_TRANSPARENT).convert('RGBA')
        
        # Preload video frames if available
        self.video_frames = []
        if HAS_OPENCV and os.path.exists(CHARACTER_VIDEO):
            self._preload_video()
        
        self._show_settings()

    def _preload_video(self):
        """Preload video frames, chroma-key black background."""
        cap = cv2.VideoCapture(CHARACTER_VIDEO)
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGBA)
            # Chroma key: near-black → transparent
            mask = (frame[:,:,0] < 25) & (frame[:,:,1] < 25) & (frame[:,:,2] < 25)
            frame[mask, 3] = 0
            pil_img = Image.fromarray(frame, 'RGBA')
            self.video_frames.append(pil_img)
        cap.release()

    # ── Settings ───────────────────────────────────────
    def _show_settings(self):
        self.settings_win = tk.Toplevel(self.root)
        self.settings_win.title("Hydration Buddy 💧")
        self.settings_win.geometry("340x260")
        self.settings_win.resizable(False, False)
        self.settings_win.configure(bg="#FFFFFF")
        self.settings_win.eval("tk::PlaceWindow . center")
        self.settings_win.attributes('-topmost', True)

        iv = tk.IntVar(value=30)
        mv = tk.StringVar(value="video" if self.video_frames else "image")

        tk.Label(self.settings_win, text="💧 Hydration Buddy", font=("Segoe UI", 16, "bold"),
                 bg="white", fg="#1a1a2e").pack(pady=(20, 5))
        tk.Label(self.settings_win, text="Transparent desktop pet — floats on your screen",
                 font=("Segoe UI", 9), bg="white", fg="#666").pack(pady=(0, 15))

        tk.Label(self.settings_win, text="Remind me every:", font=("Segoe UI", 11, "bold"),
                 bg="white", fg="#1a1a2e").pack()
        tf = tk.Frame(self.settings_win, bg="white"); tf.pack()
        tk.Radiobutton(tf, text="30 Min", variable=iv, value=30, bg="white",
                       font=("Segoe UI", 10), selectcolor="white").pack(side=tk.LEFT, padx=10)
        tk.Radiobutton(tf, text="1 Hour", variable=iv, value=60, bg="white",
                       font=("Segoe UI", 10), selectcolor="white").pack(side=tk.LEFT, padx=10)

        tk.Label(self.settings_win, text="Buddy style:", font=("Segoe UI", 11, "bold"),
                 bg="white", fg="#1a1a2e").pack(pady=(15, 5))
        mf = tk.Frame(self.settings_win, bg="white"); mf.pack()
        if self.video_frames:
            tk.Radiobutton(mf, text="🎬 Animated", variable=mv, value="video",
                           bg="white", font=("Segoe UI", 10), selectcolor="white").pack(side=tk.LEFT, padx=10)
        tk.Radiobutton(mf, text="🖼️ Static", variable=mv, value="image",
                       bg="white", font=("Segoe UI", 10), selectcolor="white").pack(side=tk.LEFT, padx=10)

        tk.Button(self.settings_win, text="🚀 Start", bg="#2196F3", fg="white",
                  font=("Segoe UI", 11, "bold"), bd=0, padx=20, pady=8, cursor="hand2",
                  command=lambda: self._start(iv.get(), mv.get())).pack(pady=20)

        self.settings_win.protocol("WM_DELETE_WINDOW", self.root.quit)

    def _start(self, interval, mode):
        self.interval_minutes = interval
        self.media_mode = mode
        self.settings_win.withdraw()
        self.running = True
        self._schedule_pet(interval * 60)

    def _schedule_pet(self, seconds):
        """Schedule the pet to appear after `seconds`."""
        if self.timer_id:
            self.root.after_cancel(self.timer_id)
        self.timer_id = self.root.after(seconds * 1000, self._show_pet)

    # ── Pet Display ────────────────────────────────────
    def _show_pet(self):
        """Show the transparent pet overlay."""
        if not self.running:
            return

        # Position: bottom-right
        screen_w = self.root.winfo_screenwidth()
        screen_h = self.root.winfo_screenheight()
        x = screen_w - WINDOW_W - 15
        y = screen_h - WINDOW_H - 50

        # Calculate button click zones
        btn_w = 125
        total_btn_w = btn_w * 2 + 10
        start_x = (WINDOW_W - total_btn_w) // 2
        panel_y = WINDOW_H - BTN_PANEL_H
        btn_cy = panel_y + (BTN_PANEL_H - BTN_H) // 2

        click_zones = {
            'drank': (start_x, btn_cy, start_x + btn_w, btn_cy + BTN_H),
            'snooze': (start_x + btn_w + 10, btn_cy, start_x + btn_w * 2 + 10, btn_cy + BTN_H),
            # Rest of the window area acts as a general click-to-dismiss zone
        }

        self.pet_window = TransparentWindow(
            WINDOW_W, WINDOW_H, x, y,
            click_zones=click_zones,
            on_click=self._on_pet_click,
        )
        self.pet_window.show()

        # Start rendering
        self.pet_active = True
        self._video_idx = 0
        self._render_loop()

    def _on_pet_click(self, zone_name):
        """Handle clicks on the pet window."""
        if zone_name == 'drank':
            self._drank_water()
        elif zone_name == 'snooze':
            self._snooze()
        elif zone_name == 'dismiss':
            self._snooze()  # Right-click dismiss = snooze

    def _render_loop(self):
        """Continuous render loop for animation."""
        if not self.pet_active or not self.pet_window:
            return

        # Get character image
        char_img = self.char_drinking or self.char_standing
        if self.media_mode == "video" and self.video_frames:
            self._video_idx = (self._video_idx + 1) % len(self.video_frames)
            char_img = self.video_frames[self._video_idx]

        # Compose frame
        frame = create_pet_frame(char_img)
        self.pet_window.update(frame)

        # Schedule next frame
        delay = 50 if (self.media_mode == "video" and self.video_frames) else 100
        self._render_id = self.root.after(delay, self._render_loop)

    # ── Actions ────────────────────────────────────────
    def _drank_water(self):
        """Close pet, show follow-up."""
        self.pet_active = False
        if self._render_id:
            self.root.after_cancel(self._render_id)
        if self.pet_window:
            self.pet_window.close()
            self.pet_window = None
        self._show_great_job()

    def _snooze(self):
        """Snooze for 10 minutes."""
        self.pet_active = False
        if self._render_id:
            self.root.after_cancel(self._render_id)
        if self.pet_window:
            self.pet_window.close()
            self.pet_window = None
        self._schedule_pet(10 * 60)

    def _show_great_job(self):
        self.gj_win = tk.Toplevel(self.root)
        self.gj_win.title("Great Job!")
        self.gj_win.geometry("280x130")
        self.gj_win.resizable(False, False)
        self.gj_win.configure(bg="white")
        self.gj_win.attributes('-topmost', True)
        self.gj_win.eval("tk::PlaceWindow . center")

        tk.Label(self.gj_win, text="🎉 Great job staying hydrated!",
                 font=("Segoe UI", 11, "bold"), bg="white", fg="#1a1a2e").pack(pady=(15, 5))
        tk.Label(self.gj_win, text="When should I remind you next?",
                 font=("Segoe UI", 10), bg="white", fg="#666").pack(pady=(0, 15))

        bf = tk.Frame(self.gj_win, bg="white"); bf.pack()
        tk.Button(bf, text="30 Mins", bg="#2196F3", fg="white", font=("Segoe UI", 10, "bold"),
                  bd=0, padx=15, pady=6, command=lambda: self._set_next(30)).pack(side=tk.LEFT, padx=10)
        tk.Button(bf, text="1 Hour", bg="#2196F3", fg="white", font=("Segoe UI", 10, "bold"),
                  bd=0, padx=15, pady=6, command=lambda: self._set_next(60)).pack(side=tk.LEFT, padx=10)

    def _set_next(self, minutes):
        self.gj_win.destroy()
        self._schedule_pet(minutes * 60)

    def run(self):
        self.root.mainloop()


# ── Entry Point ────────────────────────────────────────
if __name__ == "__main__":
    app = HydrationBuddyPet()
    app.run()
