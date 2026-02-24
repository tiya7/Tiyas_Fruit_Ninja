"""Tiya's Fruit Ninja — main game loop."""
from __future__ import annotations

import sys
import threading
import time
from collections import deque
from typing import List, Optional, Tuple

import cv2
import numpy as np

from .config import (
    BASE_SPAWN_INTERVAL, CAMERA_HEIGHT, CAMERA_INDEX, CAMERA_WIDTH,
    COMBO_MIN, COMBO_WINDOW, DIFFICULTY_RAMP, FRUIT_RADIUS,
    MAX_LIVES, MIN_SPAWN_INTERVAL, SLICE_TRAIL_MAX,
    SLICE_RADIUS_BONUS, TARGET_FPS,
)
import mediapipe as mp  # pre-import here so thread startup is instant
from mediapipe.tasks import python as _mp_pre  # noqa: F401  warm up import cache
from mediapipe.tasks.python import vision as _vision_pre  # noqa: F401
from .game_objects import FruitObj, Particle, make_particles, spawn_fruit
from .ui_overlay import draw_game_over, draw_hud, draw_particles, draw_trail, overlay_sprite

WINDOW_NAME = "Tiya's Fruit Ninja  |  Q = Quit   R = Restart"

FRUIT_COLORS = {
    "watermelon":  (40, 210,  60), "banana":     ( 0, 220, 255),
    "orange":      ( 0, 160, 255), "apple":      (30,  30, 220),
    "pineapple":   ( 0, 210, 255), "strawberry": (40,  40, 220),
    "peach":       (80, 160, 240), "cherries":   (20,  10, 200),
    "grapes":      (160, 40, 200), "mango":      ( 0, 180, 255),
    "kiwi":        (30, 185, 100), "pear":       (20, 230, 200),
    "lemon":       ( 0, 240, 255), "melon":      (40, 210, 130),
    "blueberries": (160, 60, 200),
}

def _fruit_color(sprite_name: str) -> Tuple[int,int,int]:
    return FRUIT_COLORS.get(sprite_name.replace(".png",""), (0,200,100))


# ── Loading screen ────────────────────────────────────────────────────────────

def _draw_loading(frame: np.ndarray, message: str, progress: float) -> None:
    h, w = frame.shape[:2]
    frame[:] = (15, 15, 30)

    title = "Hello and Welcome to "
    ts = 3.0
    (tw, _), _ = cv2.getTextSize(title, cv2.FONT_HERSHEY_SIMPLEX, ts, 5)
    cv2.putText(frame, title, ((w-tw)//2+3, h//3+3),
                cv2.FONT_HERSHEY_SIMPLEX, ts, (0,0,0), 6, cv2.LINE_AA)
    cv2.putText(frame, title, ((w-tw)//2, h//3),
                cv2.FONT_HERSHEY_SIMPLEX, ts, (0,220,255), 5, cv2.LINE_AA)

    sub = "Tiya's Fruit Ninja"
    ss = 1.1
    (sw,_),_ = cv2.getTextSize(sub, cv2.FONT_HERSHEY_SIMPLEX, ss, 2)
    cv2.putText(frame, sub, ((w-sw)//2, h//3+55),
                cv2.FONT_HERSHEY_SIMPLEX, ss, (150,150,200), 2, cv2.LINE_AA)

    bar_x, bar_y = w//6, h*2//3
    bar_w, bar_h = w*2//3, 22
    cv2.rectangle(frame, (bar_x, bar_y), (bar_x+bar_w, bar_y+bar_h), (50,50,80), -1)
    cv2.rectangle(frame, (bar_x, bar_y), (bar_x+bar_w, bar_y+bar_h), (80,80,120), 2)
    fill = int(bar_w * min(progress, 1.0))
    if fill > 0:
        cv2.rectangle(frame, (bar_x, bar_y), (bar_x+fill, bar_y+bar_h), (0,200,255), -1)

    ms = 0.75
    (mw,_),_ = cv2.getTextSize(message, cv2.FONT_HERSHEY_SIMPLEX, ms, 2)
    cv2.putText(frame, message, ((w-mw)//2, bar_y+55),
                cv2.FONT_HERSHEY_SIMPLEX, ms, (180,200,230), 2, cv2.LINE_AA)

    tip = "Point your index finger at the camera to slice fruit!"
    ts2 = 0.65
    (tipw,_),_ = cv2.getTextSize(tip, cv2.FONT_HERSHEY_SIMPLEX, ts2, 1)
    cv2.putText(frame, tip, ((w-tipw)//2, h-40),
                cv2.FONT_HERSHEY_SIMPLEX, ts2, (100,120,150), 1, cv2.LINE_AA)


# ── Game class ────────────────────────────────────────────────────────────────

class FruitNinja:
    def __init__(self) -> None:
        self.assets     = None
        self.tracker    = None
        self.high_score = 0          # persists across restarts
        self._reset_state()

    def _reset_state(self) -> None:
        self.fruits:    List[FruitObj] = []
        self.particles: List[Particle] = []
        self.score     = 0
        self.lives     = MAX_LIVES
        self.game_over = False
        self.trail: deque = deque(maxlen=SLICE_TRAIL_MAX)
        self.prev_tip: Optional[Tuple[int,int]] = None
        self.next_spawn     = time.time() + 1.2
        self.spawn_interval = BASE_SPAWN_INTERVAL
        self.combo_count       = 0
        self.last_slice_time   = 0.0
        self.combo_popup_text  = ""
        self.combo_popup_timer = 0.0

    def _maybe_spawn(self, w: int, h: int) -> None:
        now = time.time()
        if now < self.next_spawn:
            return
        self.fruits.append(spawn_fruit(w, h))
        self.spawn_interval = max(MIN_SPAWN_INTERVAL,
                                  BASE_SPAWN_INTERVAL - self.score * DIFFICULTY_RAMP)
        self.next_spawn = now + self.spawn_interval

    def _try_slice(self, tip: Tuple[int,int]) -> None:
        now = time.time()
        sliced_this_frame = 0

        check_points = [tip]
        if self.prev_tip is not None:
            px, py = self.prev_tip; cx, cy = tip
            for t in np.linspace(0, 1, 8):
                check_points.append((int(px+(cx-px)*t), int(py+(cy-py)*t)))

        for fruit in self.fruits:
            if fruit.sliced:
                continue
            if not any(fruit.hit_test(px, py) for px, py in check_points):
                continue
            fruit.sliced = True
            fruit.splash_timer = fruit.SPLASH_DURATION
            if fruit.is_bomb:
                self.lives = 0
                self.game_over = True
                # Update high score even on bomb death
                self.high_score = max(self.high_score, self.score)
                return
            self.score += 1
            # Update high score in real time as score increases
            self.high_score = max(self.high_score, self.score)
            sliced_this_frame += 1
            self.particles.extend(
                make_particles(fruit.x, fruit.y, _fruit_color(fruit.sprite_name)))

        if sliced_this_frame > 0:
            if now - self.last_slice_time < COMBO_WINDOW:
                self.combo_count += sliced_this_frame
            else:
                self.combo_count = sliced_this_frame
            self.last_slice_time = now
            if self.combo_count >= COMBO_MIN:
                self.combo_popup_text  = f"COMBO  x{self.combo_count}!"
                self.combo_popup_timer = 1.3

    def update(self, dt: float, tip: Optional[Tuple[int,int]], w: int, h: int) -> None:
        if self.game_over:
            return
        if tip:
            self.trail.append(tip)
            self._try_slice(tip)
        self.prev_tip = tip
        if self.combo_popup_timer > 0:
            self.combo_popup_timer -= dt
            if self.combo_popup_timer <= 0:
                self.combo_count = 0; self.combo_popup_text = ""
        self._maybe_spawn(w, h)
        for fruit in self.fruits:
            fruit.update(dt)
        keep = []
        for fruit in self.fruits:
            if fruit.is_offscreen(h, w):
                if not fruit.sliced and not fruit.is_bomb:
                    self.lives = max(0, self.lives - 1)
                    if self.lives == 0:
                        self.game_over = True
                        self.high_score = max(self.high_score, self.score)
            else:
                keep.append(fruit)
        self.fruits = keep
        self.particles = [p for p in self.particles if p.alive]
        for p in self.particles:
            p.update(dt)

    def draw(self, frame: np.ndarray) -> None:
        sprite_diam = FRUIT_RADIUS * 2

        # Finger dot feedback
        for pt in list(self.trail)[-3:]:
            cv2.circle(frame, pt, 14, (0,255,80),   -1, cv2.LINE_AA)
            cv2.circle(frame, pt,  7, (255,255,255), -1, cv2.LINE_AA)

        # Fruits
        for fruit in self.fruits:
            cx, cy = int(fruit.x), int(fruit.y)
            if fruit.sliced and fruit.splash_timer > 0:
                t = fruit.splash_timer / fruit.SPLASH_DURATION
                overlay_sprite(frame, self.assets.get("splash.png"), cx, cy,
                               int(sprite_diam*(1.8+(1-t)*0.9)), alpha_mul=t*0.9)
            elif not fruit.sliced:
                overlay_sprite(frame, self.assets.get(fruit.sprite_name),
                               cx, cy, sprite_diam)

        draw_particles(frame, self.particles)
        draw_trail(frame, list(self.trail))

        combo_label = self.combo_popup_text if self.combo_popup_timer > 0 else None
        draw_hud(frame, self.score, self.lives,
                 self.assets.get("life.png"),
                 high_score=self.high_score,
                 combo=self.combo_count,
                 combo_label=combo_label)

        if self.game_over:
            draw_game_over(frame, self.score, high_score=self.high_score)


# ── Entry point ───────────────────────────────────────────────────────────────

def main() -> None:
    cap = cv2.VideoCapture(CAMERA_INDEX)
    if not cap.isOpened():
        print(f"\n[ERROR] Cannot open camera index {CAMERA_INDEX}.")
        print("  → Change CAMERA_INDEX in src/config.py (try 1 or 2).")
        sys.exit(1)

    cap.set(cv2.CAP_PROP_FRAME_WIDTH,  CAMERA_WIDTH)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, CAMERA_HEIGHT)
    cap.set(cv2.CAP_PROP_FPS, TARGET_FPS)

    actual_w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    actual_h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    cv2.namedWindow(WINDOW_NAME, cv2.WINDOW_NORMAL)
    cv2.resizeWindow(WINDOW_NAME, actual_w, actual_h)
    cv2.setWindowProperty(WINDOW_NAME, cv2.WND_PROP_TOPMOST, 1)

    loading_frame = np.zeros((actual_h, actual_w, 3), dtype=np.uint8)
    game   = FruitNinja()
    status = {"msg": "Loading sprites...", "progress": 0.05, "done": False}

    def _load():
        from .asset_utils import AssetManager
        from .hand_tracker import HandTracker
        status["msg"] = "Generating fruit sprites..."
        status["progress"] = 0.1
        game.assets = AssetManager()
        status["msg"] = "Loading hand tracker model..."
        status["progress"] = 0.7
        game.tracker = HandTracker()
        status["msg"] = "Ready!  Get your finger in frame..."
        status["progress"] = 1.0
        time.sleep(0.6)
        status["done"] = True

    loader = threading.Thread(target=_load, daemon=True)
    loader.start()

    while not status["done"]:
        _draw_loading(loading_frame, status["msg"], status["progress"])
        cv2.imshow(WINDOW_NAME, loading_frame)
        if cv2.waitKey(30) & 0xFF in (ord("q"), 27):
            cap.release()
            cv2.destroyAllWindows()
            sys.exit(0)

    loader.join()
    game._reset_state()

    print("\n==========================================")
    print("  TIYA'S FRUIT NINJA  —  GAME STARTED!")
    print("==========================================")
    print("  • Move INDEX FINGER over fruit to slice")
    print("  • Green dot = finger position")
    print("  • Avoid the BOMB!  Q=Quit  R=Restart")
    print("==========================================\n")

    prev_time = time.time()

    while True:
        ret, frame = cap.read()
        if not ret:
            continue

        frame = cv2.flip(frame, 1)
        h, w  = frame.shape[:2]
        now   = time.time()
        dt    = min(now - prev_time, 0.05)
        prev_time = now

        tip = game.tracker.process(frame)
        game.update(dt, tip, w, h)
        game.draw(frame)
        cv2.imshow(WINDOW_NAME, frame)

        key = cv2.waitKey(1) & 0xFF
        if key in (ord("q"), 27):
            print(f"\n[INFO] Final score: {game.score}  |  Best: {game.high_score}")
            break
        if key == ord("r") and game.game_over:
            game._reset_state()          # high_score is NOT reset, only game state

    game.tracker.close()
    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
