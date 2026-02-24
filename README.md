# Webcam Fruit Ninja

A touchless Fruit Ninja clone powered by MediaPipe hand tracking and OpenCV.  
Slice fruit with your **index finger** — no mouse, no keyboard, just your webcam.

This project includes:
- A **local Python-based webcam game**
- A **website (`index.html`)** where people can explore the game and learn how to run it

---

## Project Website (Entry Point)

The file **`index.html`** is the public-facing entry point for this project.  
It showcases the Fruit Ninja game, features, controls, and setup instructions.

After enabling GitHub Pages, users can access the project website directly from their browser.

> Note: The actual game requires Python and webcam access and must be run locally.

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

# 4. Run the game (recommended)
python -m tiya.main

Important: always run the game as
python -m tiya.main

Do not run individual files directly.

Requirements (fixed)
mediapipe==0.10.32
opencv-python==4.10.0.84
numpy

These versions are tested and stable on Windows.

Controls
Input	Action
Move index finger fast	Slice fruit
Q 	Quit
R	Restart after Game Over
Project Structure
.
├── index.html           # Project website (GitHub Pages entry point)
├── assets/              # Auto-generated PNG sprites (created on first run)
├── requirements.txt
├── README.md
└── tiya/
    ├── __init__.py
    ├── config.py        # Tunable gameplay constants
    ├── asset_utils.py   # Procedural sprite generator & loader
    ├── game_objects.py  # Fruit & bomb logic, physics, spawning
    ├── hand_tracker.py  # MediaPipe hand tracking wrapper
    ├── ui_overlay.py    # HUD, trail, particles, game-over screen
    └── main.py          # Game loop
Troubleshooting
Problem	Fix
Webcam not found	Change CAMERA_INDEX in tiya/config.py (try 0, 1, 2)
Slow / laggy	Lower camera resolution in config.py
Hand not detected	Improve lighting and keep full hand visible
Import errors	Run from project root using python -m tiya.main
Gameplay Tips

Bright, even lighting improves hand detection.

Fast, confident swipes trigger slicing.

Slicing a bomb ends the game instantly.

Chain slices within ~1 second for combo multipliers.

You start with 3 lives — each missed fruit costs one.

Built with ❤️ by Tiya · Fixed & extended for MediaPipe 0.10.32+
