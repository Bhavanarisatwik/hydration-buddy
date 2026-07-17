# 💧 Hydration Buddy — Desktop Pet

A **transparent desktop pet** that floats on your screen and reminds you to drink water! Built with Python, Win32 layered windows for true per-pixel alpha transparency, and a custom pixel art character.

## ✨ Features

- **True Transparency** — Per-pixel alpha via `UpdateLayeredWindow`. The character floats with NO background, like a desktop mascot
- **Animated** — Plays a looping walk+drink animation from video or shows a static sprite
- **Thought Bubble** — "💧 Time to drink water!" appears above the character
- **Clickable Buttons** — "✓ Yes, I drank it!" and "⏰ Snooze (10 min)"
- **Draggable** — Click & drag the pet anywhere on screen
- **Right-click Dismiss** — Quickly snooze with a right-click
- **Flexible Intervals** — 30 minutes or 1 hour between reminders

## 🚀 Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Run
python water_reminder.py
```

## 🎨 How It Looks

```
┌─────────────────────────────┐
│  ┌───────────────────────┐  │  ← Blue thought bubble
│  │ 💧 Time to drink ...  │  │     (semi-transparent)
│  └───────────────────────┘  │
│                             │
│       ┌─────────┐           │
│       │         │           │  ← Character with
│       │  🚶‍♂️    │           │     TRANSPARENT background
│       │  💧     │           │
│       └─────────┘           │
│                             │
│  ┌──────────┐ ┌──────────┐  │  ← Clickable buttons
│  │ ✓ Drank! │ │ ⏰Snooze │  │
│  └──────────┘ └──────────┘  │
└─────────────────────────────┘
```

## 🛠️ How It Works

1. **Settings** → Pick interval and mode, hit Start
2. **Timer runs** in the background  
3. **Pet appears** in bottom-right corner with transparent background
4. **Click "Yes, I drank it!"** → "Great job!" + next interval
5. **Click "Snooze"** or **right-click** → reminded in 10 minutes
6. **Drag** the pet anywhere you want it

## 📁 Project Structure

```
hydration-buddy/
├── assets/
│   ├── character_transparent.png        # Standing sprite (alpha)
│   ├── character_drinking_transparent.png # Drinking sprite (alpha)
│   └── character_walk.mp4              # Animated video
├── water_reminder.py                   # Main app
├── requirements.txt
└── README.md
```

## 🔧 Tech Stack

- **Python 3.9+** 
- **pywin32** — Win32 layered windows for true alpha transparency
- **Pillow** — Image processing & frame compositing
- **OpenCV** — Video frame extraction (optional, for animated mode)

## 📝 License

MIT

---

Made with 💧 by [Satwik Bhavanari](https://github.com/Bhavanarisatwik)
