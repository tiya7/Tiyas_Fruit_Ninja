# 🍉 Tiya's Fruit Ninja — Webcam Edition

A touchless Fruit Ninja clone powered by **MediaPipe AI hand tracking** and **OpenCV**.  
Slice fruit with your **index finger** — no mouse, no controller, just your webcam.

🌐 **Live Website:** [tiya7.github.io/Tiyas_Fruit_Ninja](https://tiya7.github.io/Tiyas_Fruit_Ninja)  
📁 **GitHub:** [github.com/tiya7/Tiyas_Fruit_Ninja](https://github.com/tiya7/Tiyas_Fruit_Ninja)

---

## Quick Setup (Windows — VS Code / PowerShell)

```powershell
# 1. Clone the repo
git clone https://github.com/tiya7/Tiyas_Fruit_Ninja.git
cd Tiyas_Fruit_Ninja

# 2. Create & activate a virtual environment
py -3 -m venv .venv
.venv\Scripts\Activate.ps1

# 3. Install dependencies
pip install mediapipe==0.10.32 opencv-python numpy

# 4. Run the game
python -m tiya.main
```

> **Important:** always run as `python -m tiya.main`, not `python tiya/main.py`.  
> On first run the AI hand tracking model (~8 MB) downloads automatically — one time only.

---

## Every Time After First Setup

Only 3 commands needed:
```powershell
cd Tiyas_Fruit_Ninja
.venv\Scripts\Activate.ps1
python -m tiya.main
```

---

## Controls

| Action | Key |
|--------|-----|
| Slice fruit | Move **index finger** over it |
| Quit | `Q` or `Esc` |
| Restart after Game Over | `R` |

---

## Gameplay Features

- 🍉 **15 vibrant fruits** — watermelon, banana, orange, apple, pineapple, grapes, strawberry, peach, cherries, mango, kiwi, pear, lemon, melon, blueberries
- 💣 **Bombs** — slice one and it's instant game over
- ⚡ **Combo system** — chain slices within 1 second for multipliers
- 🏆 **High score tracker** — your personal best shown live on screen with "New Record!" celebration
- 💚 **Finger dot feedback** — green dot shows exactly where the game sees your finger
- 🎨 **Photorealistic sprites** — hand-crafted with specular highlights, rim lighting, and skin texture

---

## Project Structure

```
Tiyas_Fruit_Ninja/
├── index.html           # Landing website (GitHub Pages)
├── requirements.txt
├── README.md
└── tiya/
    ├── __init__.py
    ├── config.py        # All tunable gameplay constants
    ├── asset_utils.py   # Procedural sprite generator (parallel, cached)
    ├── game_objects.py  # Fruit/bomb physics, spawn helpers, hit detection
    ├── hand_tracker.py  # MediaPipe Tasks API wrapper (0.10.32 compatible)
    ├── ui_overlay.py    # HUD, blade trail, particles, game-over screen
    └── main.py          # Game loop + loading screen
```

---

## Troubleshooting

| Problem | Fix |
|---------|-----|
| Webcam not found | Change `CAMERA_INDEX` in `tiya/config.py` (try 0, 1, 2) |
| Slow / laggy | Lower `CAMERA_WIDTH/HEIGHT` in `tiya/config.py` |
| Hand not detected | Improve lighting; ensure full hand is visible in frame |
| `ModuleNotFoundError` | Run as `python -m tiya.main` from the project root |
| Model download fails | Requires internet on first run only |

---

## Gameplay Tips

- Bright, even front-lighting helps MediaPipe detect your hand clearly
- Watch the **green dot** — that's exactly where the game thinks your finger is
- Any deliberate movement over a fruit slices it — no fast swipe needed
- Avoid the **black bomb** at all costs — it ends the game instantly
- You have **3 lives** — each fruit that falls off-screen costs one
- Chain slices quickly to trigger **COMBO** bonuses

---

## Requirements

```
mediapipe==0.10.32
opencv-python
numpy
```

---

Built with 💚 by **Tiya** · Powered by MediaPipe + OpenCV
