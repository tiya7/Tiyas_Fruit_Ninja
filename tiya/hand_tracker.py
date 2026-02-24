"""
MediaPipe hand tracking — uses the NEW Tasks API (mediapipe 0.10.x).
Optimised for fast startup:
  - Model loaded from bytes in memory (no redundant disk seek)
  - VIDEO mode used instead of IMAGE mode (faster per-frame inference)
  - Imports cached at module level so __init__ is near-instant
"""
from __future__ import annotations

import sys
import time
import urllib.request
from pathlib import Path
from typing import Optional, Tuple

import cv2
import mediapipe as mp
import numpy as np

from .config import (
    MP_DETECTION_CONFIDENCE,
    MP_MAX_HANDS,
    MP_TRACKING_CONFIDENCE,
    INDEX_TIP_LANDMARK,
)

# ── Pre-import mediapipe submodules at module load time ───────────────────────
# Doing this here (once) instead of inside __init__ saves ~0.3s per game start.
from mediapipe.tasks import python as _mp_python
from mediapipe.tasks.python import vision as _vision

# ── Model path ────────────────────────────────────────────────────────────────
_MODEL_URL  = (
    "https://storage.googleapis.com/mediapipe-models/"
    "hand_landmarker/hand_landmarker/float16/1/hand_landmarker.task"
)
_MODEL_PATH = Path(__file__).parent.parent / "assets" / "hand_landmarker.task"


def _ensure_model() -> str:
    _MODEL_PATH.parent.mkdir(parents=True, exist_ok=True)
    if not _MODEL_PATH.exists():
        print("[INFO] Downloading hand landmarker model (~8 MB) — one time only...")
        try:
            urllib.request.urlretrieve(_MODEL_URL, str(_MODEL_PATH))
            print("[INFO] Model downloaded.")
        except Exception as e:
            print(f"\n[ERROR] Could not download MediaPipe model: {e}")
            print(f"  Download manually from:\n  {_MODEL_URL}")
            print(f"  Save to: {_MODEL_PATH}")
            sys.exit(1)
    return str(_MODEL_PATH)


# ── HandTracker ───────────────────────────────────────────────────────────────

class HandTracker:
    def __init__(self) -> None:
        model_path = _ensure_model()

        # VIDEO mode reuses internal state across frames → faster than IMAGE mode
        options = _vision.HandLandmarkerOptions(
            base_options=_mp_python.BaseOptions(model_asset_path=model_path),
            running_mode=_vision.RunningMode.VIDEO,
            num_hands=MP_MAX_HANDS,
            min_hand_detection_confidence=MP_DETECTION_CONFIDENCE,
            min_hand_presence_confidence=MP_DETECTION_CONFIDENCE,
            min_tracking_confidence=MP_TRACKING_CONFIDENCE,
        )
        self._landmarker  = _vision.HandLandmarker.create_from_options(options)
        self._last_result = None
        self._start_ms    = int(time.time() * 1000)   # for VIDEO timestamp

    def process(self, frame_bgr: np.ndarray) -> Optional[Tuple[int, int]]:
        """Return (x, y) pixel coords of index finger tip, or None."""
        h, w = frame_bgr.shape[:2]

        rgb      = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb)

        # VIDEO mode requires a monotonically increasing timestamp in ms
        timestamp_ms = int(time.time() * 1000) - self._start_ms
        result = self._landmarker.detect_for_video(mp_image, timestamp_ms)
        self._last_result = result

        if not result.hand_landmarks:
            return None

        tip = result.hand_landmarks[0][INDEX_TIP_LANDMARK]
        return (int(tip.x * w), int(tip.y * h))

    def close(self) -> None:
        self._landmarker.close()
