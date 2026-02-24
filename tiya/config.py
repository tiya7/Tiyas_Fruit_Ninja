"""Tunable gameplay constants for Webcam Fruit Ninja."""
from pathlib import Path

# ── Paths ──────────────────────────────────────────────────────────────────
BASE_DIR = Path(__file__).resolve().parent.parent
ASSET_DIR = BASE_DIR / "assets"

# ── Camera ─────────────────────────────────────────────────────────────────
CAMERA_INDEX = 0
CAMERA_WIDTH = 1280
CAMERA_HEIGHT = 720
TARGET_FPS = 60

# ── Physics ────────────────────────────────────────────────────────────────
GRAVITY = 1400           # pixels / s²
MIN_LAUNCH_VY = -1000   # px/s  (negative = upward)
MAX_LAUNCH_VY = -750
MIN_LAUNCH_VX = -200
MAX_LAUNCH_VX = 200
FRUIT_RADIUS = 75        # bigger = easier to hit

# ── Fruit spawn ────────────────────────────────────────────────────────────
BASE_SPAWN_INTERVAL = 1.6
MIN_SPAWN_INTERVAL = 0.6
DIFFICULTY_RAMP = 0.0003

# ── Slicing ────────────────────────────────────────────────────────────────
SLICE_MIN_SPEED = 0       # NO speed requirement — any touch slices
SLICE_TRAIL_MAX = 40
SLICE_RADIUS_BONUS = 20   # extra px added to FRUIT_RADIUS for hit detection

# ── Scoring / combo ────────────────────────────────────────────────────────
COMBO_WINDOW = 1.2
COMBO_MIN = 2

# ── Lives ──────────────────────────────────────────────────────────────────
MAX_LIVES = 3

# ── HUD ────────────────────────────────────────────────────────────────────
HUD_COLOR = (30, 55, 90)
HUD_ALPHA = 0.72
FONT = 0                    # cv2.FONT_HERSHEY_SIMPLEX

# ── Hand tracking ──────────────────────────────────────────────────────────
MP_MAX_HANDS = 1
MP_DETECTION_CONFIDENCE = 0.5
MP_TRACKING_CONFIDENCE  = 0.5
INDEX_TIP_LANDMARK = 8
