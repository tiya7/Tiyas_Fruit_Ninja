# Webcam Fruit Ninja

A touchless Fruit Ninja clone powered by MediaPipe hand tracking and OpenCV.  
Slice fruit with your **index finger** — no mouse, no keyboard, just your webcam.

---

## Quick Setup (Windows — VS Code / PowerShell)

```powershell
# 1. Create & activate a virtual environment
py -3 -m venv .venv
.venv\Scripts\Activate.ps1

# 2. Upgrade pip (important!)
pip install --upgrade pip

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run the game (MUST use -m flag for relative imports)
python -m src.main
```

> **Important:** always run as `python -m src.main`, not `python src/main.py`.

---

## Requirements (fixed)

```
mediapipe==0.10.32
opencv-python==4.10.0.84
numpy
```

The original `requirements.txt` pinned `mediapipe==0.10.14` (doesn't exist)
and `numpy==1.26.4` (requires a C compiler on Windows). Both are fixed here.

---

## Controls

| Key | Action |
|-----|--------|
| Move index finger fast | Slice fruit |
| `Q` / `Esc` | Quit |
| `R` | Restart after Game Over |

---

## Project Structure

```
.
├── assets/              # Auto-generated PNG sprites (created on first run)
├── requirements.txt
├── README.md
└── src/
    ├── __init__.py
    ├── config.py        # Tunable gameplay constants
    ├── asset_utils.py   # Procedural sprite generator & loader
    ├── game_objects.py  # Fruit/bomb dataclasses, physics, spawn helpers
    ├── hand_tracker.py  # MediaPipe wrapper (compatible with 0.10.32)
    ├── ui_overlay.py    # HUD, trail, particles, game-over screen
    └── main.py          # Game loop
```

---

## Troubleshooting

| Problem | Fix |
|---------|-----|
| Webcam not found | Change `CAMERA_INDEX` in `src/config.py` (try 0, 1, 2) |
| Slow / laggy | Lower `CAMERA_WIDTH/HEIGHT` in `src/config.py` |
| Hand not detected | Better lighting; make sure full hand is in frame |
| `ModuleNotFoundError` | Run as `python -m src.main` from the project root |

---

## Gameplay Tips

- Bright, even front-lighting helps MediaPipe see your hand clearly.
- Fast, decisive slicing motions trigger the slice — slow drags don't.
- Hitting a bomb ends the game instantly — dodge them!
- Chain slices within ~1 second to trigger combo multipliers.
- You have 3 lives; each fruit that falls off-screen costs one.

---

Built with ❤️ by **tubakhxn** · Fixed & extended for mediapipe 0.10.32+
