# 💧 Hydration Buddy

A desktop water reminder app featuring a custom pixel art character that pops up to remind you to stay hydrated!

Built with Python, Tkinter, and OpenCV.

## ✨ Features

- **Custom Pixel Art Character** — Your own animated hydration buddy
- **Two Modes** — Animated video loop or static PNG character
- **Flexible Intervals** — Remind every 30 minutes or 1 hour
- **Snooze** — Busy? Snooze for 10 minutes
- **Encouragement** — "Great job!" acknowledgement when you drink
- **Borderless Popup** — Clean, modern overlay in the bottom-right corner
- **Draggable** — Move the reminder window anywhere on screen

## 📸 Preview

<!-- Add screenshots here -->

## 🚀 Quick Start

### 1. Install Python

Download and install Python 3.9+ from [python.org](https://python.org).  
**Check "Add Python to PATH" during installation.**

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Run

```bash
python water_reminder.py
```

Or simply double-click `water_reminder.py`!

## 🎨 Customize Your Character

Replace the files in `assets/` with your own pixel art:

| File | Purpose |
|------|---------|
| `assets/character.png` | Static standing pose |
| `assets/character_drinking.png` | Drinking pose (shown in reminder) |
| `assets/character_walk.mp4` | Animated walking/drinking video |

## 🏗️ Project Structure

```
hydration-buddy/
├── assets/
│   ├── character.png           # Standing sprite
│   ├── character_drinking.png  # Drinking sprite
│   ├── character_phone.png     # Phone sprite
│   └── character_walk.mp4      # Animated video
├── water_reminder.py           # Main application
├── requirements.txt            # Python dependencies
└── README.md
```

## ⚙️ How It Works

1. Launch the app → settings window appears
2. Choose your interval (30 min / 1 hour) and style (animated / static)
3. Click "Start Reminding Me!" → app minimizes to background
4. When time's up → your character pops up in the bottom-right with "💧 Time to drink water!"
5. Click **"Yes, I drank it!"** → see "Great job!" and set next reminder
6. Click **"Snooze"** → reminded again in 10 minutes

## 🛠️ Tech Stack

- **Python 3.9+** — Core language
- **Tkinter** — Built-in GUI framework
- **Pillow** — Image handling
- **OpenCV** — Video playback (optional, for animated mode)

## 📝 License

MIT — feel free to use, modify, and share!

---

Made with 💧 by [Satwik Bhavanari](https://github.com/Bhavanarisatwik)
